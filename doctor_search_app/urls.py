from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginRequestView,
    LoginVerifyView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    DoctorViewSet,
    ReviewViewSet
)

# Create a router for the ViewSets (Doctors and Reviews)
router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    # --- Auth Endpoints ---
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginRequestView.as_view(), name='auth_login_request'),       # Step 1: Send OTP
    path('auth/verify/', LoginVerifyView.as_view(), name='auth_login_verify'),         # Step 2: Verify OTP
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # --- Router Endpoints (Doctors & Reviews) ---
    # This includes /doctors/, /doctors/{id}/, /reviews/, etc.
    path('', include(router.urls)),
]