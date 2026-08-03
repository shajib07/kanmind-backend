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
    token, _ = Token.objects.get_or_create(user=user)

    return {
        'token': token.key,
        'fullname': user.first_name,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            get_auth_response_data(user),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        return Response(
            get_auth_response_data(user),
            status=status.HTTP_200_OK,
        )


class EmailCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
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