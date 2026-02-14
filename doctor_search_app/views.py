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
from .models import Doctor, SavedDoctor


from .models import SavedDoctor
from .serializers import SavedDoctorSerializer

from .models import Doctor, Review
from .serializers import (
    UserRegistrationSerializer,
    LoginRequestSerializer,     # We will reuse this for standard login
    OTPVerifySerializer,        # We will reuse this for email verification
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    DoctorSerializer,
    ReviewSerializer
)

User = get_user_model()

# ===========================
# HELPER FUNCTIONS
# ===========================

def send_otp_email(user, otp_code, subject_prefix="Account"):
    """Sends the OTP to the user's email."""
    subject = f'{subject_prefix} Verification Code'
    message = f'Hello {user.username},\n\nYour OTP code is: {otp_code}\n\nIt expires in 10 minutes.\n\nEnter this code to verify your account.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"Email Error: {e}")

# ===========================
# AUTH VIEWS
# ===========================

class RegisterView(views.APIView):
    """Step 1: Create Account (Inactive) -> Send OTP Email"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Create the user but set to inactive until verified
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            user.is_active = False # Deactivate until email verified
            user.save()

            # Generate & Send OTP
            otp = user.generate_otp()
            send_otp_email(user, otp, subject_prefix="Activate")

            return Response({
                "message": "Account created. OTP sent to email.",
                "username": user.username
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# doctors/views.py


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
                # 1. Activate User
                user.is_active = True
                user.is_email_verified = True
                user.otp_code = None 
                user.save()

                # 2. GENERATE TOKENS (Auto-Login Logic)
                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "Email verified successfully!",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user_id": user.id,
                    "username": user.username,
                    "is_admin": user.admin
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginView(views.APIView):
    """Step 3: Standard Login (Username + Password)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # We reuse LoginRequestSerializer (username + password)
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user:
                if not user.is_active:
                    return Response({"error": "Account is not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)
                
                # Generate Tokens
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
    """Step 1 of Reset: Send OTP to Email"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                otp = user.generate_otp()
                send_otp_email(user, otp, subject_prefix="Password Reset")
            except User.DoesNotExist:
                # Security: Do not reveal if email exists
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
                user = User.objects.get(email=email)
                if user.verify_otp(otp):
                    user.set_password(new_password)
                    user.otp_code = None
                    user.save()
                    return Response({"message": "Password reset successful. Please login."}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===========================
# DOCTOR & REVIEW VIEWS
# ===========================


class ToggleSavedDoctorView(APIView):
    """
    Checks if the doctor is saved.
    If YES -> Deletes it (Unsave).
    If NO -> Creates it (Save).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=400)

        doctor = get_object_or_404(Doctor, id=doctor_id)

        # The magic happens here: get_or_create prevents the Unique Constraint error
        saved_entry, created = SavedDoctor.objects.get_or_create(user=request.user, doctor=doctor)

        if not created:
            # If it wasn't created, it meant it existed. So we delete it.
            saved_entry.delete()
            return Response({'status': 'unsaved', 'doctor_id': doctor_id})

        return Response({'status': 'saved', 'doctor_id': doctor_id})

class DoctorViewSet(viewsets.ModelViewSet):
    """
    Lists doctors ranked by their average review rating.
    Supports search and filtering.
    """
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # Search and Filter Configuration
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'specialty', 'hospital', 'location']
    filterset_fields = ['specialty', 'location']
    ordering_fields = ['average_rating', 'name']

    def get_queryset(self):
        # Annotate adds virtual fields for sorting logic
        return Doctor.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-average_rating')

# doctors/views.py

# ... existing imports ...

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Handles creating and viewing reviews.
    Supports filtering by doctor_id and 'mine=true' for current user.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        
        # Filter by Doctor
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
            
        # Filter by Current User ("My Reviews")
        if self.request.query_params.get('mine'):
            if self.request.user.is_authenticated:
                queryset = queryset.filter(user=self.request.user)
            else:
                return Review.objects.none() # Return empty if not logged in

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SavedDoctorViewSet(viewsets.ModelViewSet):
    """
    Manage user's saved doctors.
    GET /saved-doctors/ -> List all saved
    POST /saved-doctors/ -> Save a doctor (Body: {"doctor": 5})
    DELETE /saved-doctors/{id}/ -> Unsave
    """
    serializer_class = SavedDoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show doctors saved by the current user
        return SavedDoctor.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user
        serializer.save(user=self.request.user)        