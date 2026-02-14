from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Doctor, Review
from .models import SavedDoctor
from django.db.models import Avg  # <--- ADD THIS IMPORT
User = get_user_model()

# ===========================
# AUTH SERIALIZERS
# ===========================

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'age']

    def create(self, validated_data):
        # Use create_user to handle password hashing automatically
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            age=validated_data.get('age')
        )
        return user

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class OTPVerifySerializer(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField(max_length=6)

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

# ===========================
# DOCTOR & REVIEW SERIALIZERS
# ===========================

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # Add this field to see the doctor's name in the review list
    doctor_name = serializers.ReadOnlyField(source='doctor.name') 

    class Meta:
        model = Review
        fields = ['id', 'doctor', 'doctor_name', 'user', 'rating', 'comment', 'created_at']

class DoctorSerializer(serializers.ModelSerializer):
    # Use SerializerMethodField to ensure we always get a value
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialty', 'hospital', 'location', 
            'average_rating', 'review_count', 'email', 'cell', 'image'
        ]

    def get_average_rating(self, obj):
        # 1. Check if it was pre-calculated (Annotated in QuerySet)
        if hasattr(obj, 'average_rating') and obj.average_rating is not None:
            return obj.average_rating
        
        # 2. Fallback: Calculate it on the fly (For Saved Doctors list)
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return avg if avg else 0

    def get_review_count(self, obj):
        # 1. Check if pre-calculated
        if hasattr(obj, 'review_count'):
            return obj.review_count
        
        # 2. Fallback: Count manually
        return obj.reviews.count()
# Add this to serializers.py


class SavedDoctorSerializer(serializers.ModelSerializer):
    # We can nest the full doctor details so the frontend gets everything at once
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = SavedDoctor
        fields = ['id', 'doctor', 'doctor_details', 'created_at']
        read_only_fields = ['user']        