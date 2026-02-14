from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
import random
import datetime



class User(AbstractUser):
    email = models.EmailField(unique=True)
    password_digest = models.CharField(max_length=100, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    admin = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    recovery_pin = models.CharField(max_length=10, null=True, blank=True)
    otp_code = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    def generate_otp(self):
        self.otp_code = f"{random.randint(100000, 999999)}"
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp_code

    def verify_otp(self, entered_otp):
        if not self.otp_code or not self.otp_created_at: return False
        if self.otp_code != entered_otp: return False
        if timezone.now() > self.otp_created_at + datetime.timedelta(minutes=10): return False
        return True

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=100)
    hospital = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    email = models.EmailField()
    cell = models.CharField(max_length=20)
    
    # NEW FIELD FOR IMAGES
    image = models.URLField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.specialty}"

class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('doctor', 'user')

# Add this to your models.py

class SavedDoctor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_doctors')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='saved_by_users')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'doctor') # Prevent saving the same doctor twice
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.doctor.name}"       