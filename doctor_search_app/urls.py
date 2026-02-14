from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    VerifyEmailView,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    DoctorViewSet,
    ReviewViewSet,
    SavedDoctorViewSet,
    ToggleSavedDoctorView  # <--- NEW IMPORT
)

# Create a router for the ViewSets
router = DefaultRouter()
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'saved-doctors', SavedDoctorViewSet, basename='saved-doctor')

urlpatterns = [
    # --- Auth Endpoints ---
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='auth_verify'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    
    # --- Password Reset ---
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('auth/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # --- THE FIX: Toggle Endpoint ---
    # This must be defined explicitly so the frontend can call /saved-doctors/toggle/
    path('saved-doctors/toggle/', ToggleSavedDoctorView.as_view(), name='saved-doctor-toggle'),

    # --- Router Endpoints (Doctors & Reviews) ---
    path('', include(router.urls)),
]