"""API views for registration, login and email lookups."""

from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.serializers import (
    EmailCheckSerializer,
    LoginSerializer,
    RegistrationSerializer,
    UserSummarySerializer,
)


def get_auth_response_data(user):
    """Return the auth token and profile payload for a user."""
    token, _ = Token.objects.get_or_create(user=user)

    return {
        'token': token.key,
        'fullname': user.first_name,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(APIView):
    """Register a new user and return an auth token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Create the user and respond with their auth data."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            get_auth_response_data(user),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user and return an auth token."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Validate the credentials and respond with the user's auth data."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        return Response(
            get_auth_response_data(user),
            status=status.HTTP_200_OK,
        )


class EmailCheckView(APIView):
    """Look up a user by email and return their summary if found."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return the matching user's summary, or 404 if none exists."""
        serializer = EmailCheckSerializer(
            data=request.query_params
        )
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(
                {'detail': 'Email not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        response_serializer = UserSummarySerializer(user)
        return Response(response_serializer.data)
