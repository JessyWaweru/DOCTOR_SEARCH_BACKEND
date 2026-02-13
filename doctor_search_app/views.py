from rest_framework import viewsets, status, views, generics, filters, permissions
from rest_framework.response import Response
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend

from .models import Doctor, Review
from .serializers import (
    UserRegistrationSerializer,
    LoginRequestSerializer,
    OTPVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    DoctorSerializer,
    ReviewSerializer
)

User = get_user_model()

# ===========================
# HELPER FUNCTIONS
# ===========================

def send_otp_email(user, otp_code, subject_prefix="Login"):
    """Sends the OTP to the user's email."""
    subject = f'{subject_prefix} Verification Code'
    message = f'Hello {user.username},\n\nYour OTP code is: {otp_code}\n\nIt expires in 5 minutes.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    # Fail silently to avoid crashing if email settings aren't perfect yet
    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"Email Error: {e}")

# ===========================
# AUTH VIEWS
# ===========================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class LoginRequestView(views.APIView):
    """Step 1: Validate credentials -> Generate OTP -> Send Email"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)
            
            if user is not None:
                otp = user.generate_otp()
                send_otp_email(user, otp, subject_prefix="Login")
                return Response({
                    "message": "Credentials valid. OTP sent to email.",
                    "username": user.username
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginVerifyView(views.APIView):
    """Step 2: Validate OTP -> Return JWT Tokens"""
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
                # Generate SimpleJWT tokens
                refresh = RefreshToken.for_user(user)
                
                # Clear OTP to prevent replay attacks
                user.otp_code = None 
                user.save()

                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'username': user.username,
                    'is_admin': user.admin
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                # Security: Do not reveal if email exists or not
                pass
            
            return Response({"message": "If an account exists with this email, an OTP has been sent."}, status=status.HTTP_200_OK)
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
        ).order_by('-average_rating') # Default: Highest rated first

class ReviewViewSet(viewsets.ModelViewSet):
    """
    Handles creating and viewing reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optional: Filter reviews to specific doctor if 'doctor_id' is in URL params
        queryset = Review.objects.all()
        doctor_id = self.request.query_params.get('doctor_id')
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)
        return queryset

    def perform_create(self, serializer):
        # Automatically link the logged-in user to the review
        serializer.save(user=self.request.user)