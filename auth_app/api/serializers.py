"""Serializers for user registration, login and email lookups."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate sign-up data and create a new user account."""

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'fullname',
            'email',
            'password',
            'repeated_password',
        ]

    fullname = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Ensure the password and its confirmation match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Create the user, storing the full name as ``first_name``."""
        fullname = validated_data.pop('fullname')
        validated_data.pop('repeated_password')

        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        user.first_name = fullname
        user.save()
        return user

    def validate_email(self, value):
        """Reject an email address that is already registered."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists.')
        return value


class LoginSerializer(serializers.Serializer):
    """Authenticate a user from their email and password."""

    email = serializers.EmailField(required=False)
    password = serializers.CharField(
        write_only=True,
        required=False,
    )

    def validate(self, attrs):
        """Authenticate the credentials and attach the user to the data."""
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError(
                {'detail': 'Email and password are required.'}
            )
        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                {'detail': 'Invalid email or password.'}
            )
        attrs['user'] = user
        return attrs


class EmailCheckSerializer(serializers.Serializer):
    """Validate the ``email`` query parameter of the email-check endpoint."""

    email = serializers.CharField(required=False)

    def validate(self, attrs):
        """Ensure the email is present and well-formed."""
        email = attrs.get('email')
        if not email:
            raise serializers.ValidationError(
                {'detail': 'Email query parameter is required.'}
            )
        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError(
                {'detail': 'Invalid email address.'}
            )
        return attrs


class UserSummarySerializer(serializers.ModelSerializer):
    """Compact user representation used in nested API responses."""

    fullname = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullname',
        ]
