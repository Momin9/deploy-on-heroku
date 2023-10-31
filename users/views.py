import copy
from datetime import timedelta

from django.contrib.auth import get_user_model
from django_rest_passwordreset.views import ResetPasswordRequestToken as BaseResetPasswordRequestToken
from rest_auth.registration.app_settings import register_permission_classes
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from allauth.account.models import EmailAddress

from django_rest_passwordreset.models import ResetPasswordToken, get_password_reset_token_expiry_time, clear_expired
from django_rest_passwordreset.signals import pre_password_reset, post_password_reset, reset_password_token_created

from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_auth.registration.views import RegisterView

from modules.phone_verification.utils import send_verification_code, send_password_reset_token_phone, send_email_verification_key
from users.models import UserProfile
from users.utils import clear_expired_keys
from users.serializers import (UserProfileSerializer, CustomRegistrationSerializer, AuthTokenSerializer,
                               PasswordResetTokenSerializer, CustomPasswordTokenSerializer)

USER_AGENT_HEADER = getattr(settings, 'HTTP_USER_AGENT_HEADER', 'HTTP_USER_AGENT')
IP_ADDRESS_HEADER = getattr(settings, 'DJANGO_REST_PASSWORDRESET_IP_ADDRESS_HEADER', 'REMOTE_ADDR')

User = get_user_model()


class UserProfileViewSet(viewsets.ModelViewSet):
    lookup_field = 'owner'
    queryset = UserProfile.objects.none()
    serializer_class = UserProfileSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.filter(owner=self.request.user)
        return queryset

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class UserRegister(RegisterView):
    serializer_class = CustomRegistrationSerializer
    permission_classes = register_permission_classes()

    @transaction.atomic()
    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        code = data.get("code")

        serializer = self.serializer_class(data=data, context={'request': request})
        if serializer.is_valid():
            headers = self.get_success_headers(serializer.data)
            user = self.perform_create(serializer)  # will create EmailAddress/PhoneVerification entries against user.
            response = {"is_phone": False, "code": code, "username": user.username, "public_key": user.public_key}
            if serializer.username_is_phone(user.username):
                message_is_sent = send_verification_code(user)
                response.update({"is_phone": True, "message_sent": message_is_sent})
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        else:
            errors = serializer.errors

        return Response(errors, status.HTTP_400_BAD_REQUEST)


class AuthToken(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)

        auth_serializer = self.serializer_class(data=data, context={'request': request})
        if auth_serializer.is_valid():
            user = auth_serializer.validated_data['user']
            return Response(user.get_login_success_json(), status=status.HTTP_200_OK)

        return Response(auth_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordConfirm(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CustomPasswordTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data.get("password")
            token = serializer.validated_data.get("token")

            reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
            pre_password_reset.send(sender=self.__class__, user=reset_password_token.user)

            reset_password_token.user.set_password(password)
            reset_password_token.user.save()

            post_password_reset.send(sender=self.__class__, user=reset_password_token.user)
            ResetPasswordToken.objects.filter(user=reset_password_token.user).delete()
            return Response({'status': 'Password change successfully'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordRequestToken(BaseResetPasswordRequestToken):
    serializer_class = PasswordResetTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password_reset_token_validation_time = get_password_reset_token_expiry_time()
            now_minus_expiry_time = timezone.now() - timedelta(hours=password_reset_token_validation_time)
            target_user = User.objects.filter(username__iexact=username).first()
            if target_user.password_reset_tokens.all().count() > 0:
                token = target_user.password_reset_tokens.first()
            else:
                token = ResetPasswordToken.objects.create(
                    user=target_user,
                    user_agent=request.META.get(USER_AGENT_HEADER),
                    ip_address=request.META.get(IP_ADDRESS_HEADER)
                )  # exception is expected if IP_ADDRESS_HEADER is None/empty.

            if serializer.username_is_email:
                clear_expired(now_minus_expiry_time)
                reset_password_token_created.send(sender=self.__class__, instance=self, reset_password_token=token)
                _status = "Email Sent Successfully."
            else:
                clear_expired_keys(now_minus_expiry_time)
                success = send_password_reset_token_phone(token.key, username)
                _status = "Reset Password Token Sent." if success else "Something went wrong while sending message."

            return Response({'status': _status}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


def complete_view(request):
    html = render_to_string("email/user_email_confirmed.html")
    return HttpResponse(html)


def default_view(request):
    html = render_to_string("default/default.html")
    return HttpResponse(html)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_superuser(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_superuser(username=username, password=password, email=email)
    return Response({'success': 'Superuser created'}, status=status.HTTP_201_CREATED)
