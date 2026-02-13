from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import datetime
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    # Legacy compatibility
    password_digest = models.CharField(max_length=100, null=True, blank=True)
    
    age = models.IntegerField(null=True, blank=True)
    # Note: AbstractUser already has 'is_staff' and 'is_superuser'. 
    # You can keep 'admin' if it serves a specific business logic role.
    admin = models.BooleanField(default=False)

    # --- STATIC RECOVERY (Optional Backup) ---
    # A fixed pin user can use if they can't access email (optional)
    recovery_pin = models.CharField(max_length=10, null=True, blank=True)

    # --- DYNAMIC OTP FIELDS (For Login & Reset) ---
    # This code changes every time the user tries to log in
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    # --- HELPER METHODS ---

    def generate_otp(self):
        """Generates a 6-digit OTP, saves it, and updates the timestamp."""
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp_code

    def verify_otp(self, entered_otp):
        """
        Verifies the OTP and checks if it is expired (e.g., 5 min limit).
        Returns True if valid, False otherwise.
        """
        if not self.otp_code or not self.otp_created_at:
            return False
            
        # Check if OTP matches
        if self.otp_code != entered_otp:
            return False
            
        # Check expiration (e.g., 5 minutes)
        now = timezone.now()
        if now > self.otp_created_at + datetime.timedelta(minutes=5):
            return False
            
        # Optional: Clear OTP after successful use to prevent replay
        # self.otp_code = None
        # self.save()
        
        return True

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=100) # Could be a ChoiceField or ForeignKey if categories are fixed
    hospital = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    cell = models.CharField(max_length=20)
    
    # Optional: Image, Bio, etc.
    
    def __str__(self):
        return f"{self.name} - {self.specialty}"

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from reviewing the same doctor twice (optional but recommended)
        unique_together = ('doctor', 'user')    

