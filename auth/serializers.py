from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'email', 'phone', 'password', 'password_confirm',
            'full_name', 'school', 'major', 'year', 'bio',
            'avatar_url', 'learning_radius_km', 'privacy_level'
        ]
        extra_kwargs = {
            'phone': {'required': False},
            'school': {'required': False},
            'major': {'required': False},
            'year': {'required': False},
            'bio': {'required': False},
            'avatar_url': {'required': False},
            'learning_radius_km': {'required': False},
            'privacy_level': {'required': False},
        }
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")
        
        # Check if user is active
        if user.status != User.STATUS_ACTIVE:
            raise serializers.ValidationError("This account is not active.")
        
        # Verify password using Django's check_password (works with AbstractBaseUser)
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    school_name = serializers.CharField(source='school.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone', 'full_name', 'school', 'school_name',
            'major', 'year', 'bio', 'avatar_url', 'learning_radius_km',
            'privacy_level', 'status', 'last_active_at', 'created_at'
        ]
        read_only_fields = ['id', 'email', 'status', 'created_at', 'last_active_at']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validate that the old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return attrs
    
    def save(self):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user
