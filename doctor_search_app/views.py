import threading # Required for background email sending
import requests 
from rest_framework import viewsets, status, views, generics, filters, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Doctor, SavedDoctor, Review
from .serializers import (
    UserRegistrationSerializer,
    LoginRequestSerializer,
    OTPVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    DoctorSerializer,
    ReviewSerializer,
    SavedDoctorSerializer
)

User = get_user_model()

# ===========================
# HELPER FUNCTIONS
# ===========================



def send_email_async(subject, message, recipient_list):
    """Sends email via Resend API instead of SMTP"""
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    sender_email = settings.DEFAULT_FROM_EMAIL or "onboarding@resend.dev"
    data = {
        "from": sender_email,
        "to": recipient_list,
        "subject": subject,
        "html": f"<p>{message}</p>"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            print(f"✅ Email sent via Resend from: {sender_email}")
        else:
            print(f"❌ Resend Error: {response.text}")
    except Exception as e:
        print(f"❌ Background API Error: {e}")

# ... keep the rest of your send_otp_email and Threading logic the same ...

def send_otp_email(user, otp_code, subject_prefix="Account"):
    """
    Triggers an asynchronous email thread.
    This prevents 'CRITICAL WORKER TIMEOUT' on Render.
    """
    subject = f'{subject_prefix} Verification Code'
    message = (
        f'Hello {user.username},\n\n'
        f'Your OTP code is: {otp_code}\n\n'
        f'It expires in 10 minutes.\n\n'
        f'Enter this code to verify your account.'
    )
    recipient_list = [user.email]
    
    # Start the thread
    thread = threading.Thread(
        target=send_email_async, 
        args=(subject, message, recipient_list)
    )
    thread.start()

# ===========================
# AUTH VIEWS
# ===========================

class RegisterView(views.APIView):
    """Step 1: Create Account (Inactive) -> Send OTP Email via Thread"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            user.is_active = False 
            user.save()

            # Generate OTP
            otp = user.generate_otp()
            
            # This is now non-blocking (Fast response)
            send_otp_email(user, otp, subject_prefix="Activate")

            return Response({
                "message": "Account created. OTP sent to email.",
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(views.APIView):
    """Step 2: Verify OTP -> Activate Account -> Auto Login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            otp_input = serializer.validated_data['otp']

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if user.verify_otp(otp_input):
                user.is_active = True
                user.is_email_verified = True
                user.otp_code = None 
                user.save()

                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "Email verified successfully!",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "username": user.username
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(views.APIView):
    """Standard Login"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Allow login with Email
            if '@' in username:
                try:
                    # Use __iexact for case-insensitive lookup
                    user_obj = User.objects.get(email__iexact=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    print(f"Login Warning: No user found for email '{username}'")
                    pass 

            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    return Response({"error": "Account is not verified."}, status=status.HTTP_403_FORBIDDEN)
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===========================
# PASSWORD RESET VIEWS
# ===========================

class PasswordResetRequestView(views.APIView):
    """Step 1 of Reset: Send OTP to Email via Thread"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                otp = user.generate_otp()
                # Fast response, background email
                send_otp_email(user, otp, subject_prefix="Password Reset")
            except User.DoesNotExist:
                pass
            
            return Response({"message": "If an account exists, an OTP has been sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(views.APIView):
    """Step 2 of Reset: Verify OTP -> Change Password"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            new_password = serializer.validated_data['new_password']

            try:
                user = User.objects.get(email__iexact=email)
                if user.verify_otp(otp):
                    user.set_password(new_password)
                    user.otp_code = None
                    user.save()
                    return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===========================
# DOCTOR & REVIEW VIEWS
# ===========================

class ToggleSavedDoctorView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=400)

        doctor = get_object_or_404(Doctor, id=doctor_id)
        saved_entry, created = SavedDoctor.objects.get_or_create(user=request.user, doctor=doctor)

        if not created:
            saved_entry.delete()
            return Response({'status': 'unsaved', 'doctor_id': doctor_id})

        return Response({'status': 'saved', 'doctor_id': doctor_id})

class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'specialty', 'hospital', 'location']
    filterset_fields = ['specialty', 'location']
    ordering_fields = ['average_rating', 'name']

    def get_queryset(self):
        return Doctor.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-average_rating')

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        if self.request.query_params.get('mine'):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(user=self.request.user)
            else:
                return Review.objects.none()
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavedDoctorViewSet(viewsets.ModelViewSet):
    serializer_class = SavedDoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SavedDoctor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)