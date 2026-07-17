from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
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
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class UserSummarySerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'fullname',
        ]









