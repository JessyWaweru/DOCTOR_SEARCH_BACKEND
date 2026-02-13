from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Doctor, Review

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
    user = serializers.StringRelatedField(read_only=True)  # Show username, not ID

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class DoctorSerializer(serializers.ModelSerializer):
    # These fields are calculated in the ViewSet using annotate()
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'specialty', 'hospital', 
            'location', 'email', 'cell', 
            'average_rating', 'review_count'
        ]