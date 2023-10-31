from datetime import timedelta

from allauth.account.utils import setup_user_email
from phonenumbers import NumberParseException

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password, get_password_validators
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django_rest_passwordreset.models import get_password_reset_token_expiry_time, ResetPasswordToken

from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer as BaseAuthTokenSerializer
from django_rest_passwordreset.serializers import EmailSerializer, PasswordTokenSerializer
from users.models import UserProfile
from rest_auth.registration.serializers import RegisterSerializer

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress

from users.utils import is_valid_email, user_already_registered
from modules.phone_verification.models import PhoneVerification
from modules.phone_verification.utils import is_valid_phone_number, send_email_verification_key, \
    recreate_new_user_key, get_validated_phone_number_with_code

User = get_user_model()

USER_NAME_FIELD = 'username'
REGION_CODE_FIELD = 'code'


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='owner.username', required=True)
    email = serializers.CharField(source='owner.email', read_only=True)
    phone_no = serializers.CharField(source='owner.phone', read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data.get('image') is None:
            instance.image = instance.image
        else:
            instance.image = validated_data.pop('image')
        instance.owner.username = validated_data.pop('username', instance.owner.username)
        instance.name = validated_data.pop('name', instance.name)
        instance.address = validated_data.pop('address', instance.address)
        instance.lng = validated_data.pop('lng', instance.lng)
        instance.lat = validated_data.pop('lat', instance.lat)
        instance.save()
        return instance


class CustomValidationMixin:

    @staticmethod
    def perform_login_validations(data):
        username = data.get(USER_NAME_FIELD)
        code = data.get(REGION_CODE_FIELD)

        email_or_phone = username
        email_is_valid, number_is_valid = is_valid_email(email_or_phone), is_valid_phone_number(email_or_phone)

        error = {}
        if not email_is_valid and not code:
            error = err_msg("code", "Please Provide a Country Code.")
        if not email_is_valid and not number_is_valid:
            error = err_msg("code", "Please provide a valid Email/Number.")

        return error, email_is_valid, number_is_valid

    @staticmethod
    def perform_signup_validations(data):
        username = data.get(USER_NAME_FIELD)

        error, email_is_valid, number_is_valid = CustomValidationMixin.perform_login_validations(data)

        if error:
            return error, email_is_valid, number_is_valid

        # check if user with same email/phone_number already exists.
        if user_already_registered(username):
            error = err_msg("username", "A user with that Email/Number already exists.")

        return error, email_is_valid, number_is_valid

    def username_is_email(self, username):
        return is_valid_email(username)

    def username_is_phone(self, username):
        return not self.username_is_email(username)


class CustomRegistrationSerializer(RegisterSerializer, CustomValidationMixin):  # noqa
    username = serializers.CharField(
        help_text=_("You can enter an email or a phone number. (e.g. abc@abc.com / +92123456879)"),
        label=_("Email/Phone"),
        required=True)
    code = serializers.CharField(required=True, label=_("Country Code"))
    email = serializers.HiddenField(required=False, default="")  # overriding super's field
    password2 = serializers.HiddenField(required=False, default="")  # overriding super's field

    def validate(self, data):
        username = data.get(USER_NAME_FIELD)
        username = get_validated_phone_number_with_code(data.get("code"), username) \
            if not self.username_is_email(username) else username
        data[USER_NAME_FIELD] = username

        error, email_is_valid, number_is_valid = self.perform_signup_validations(data)
        if error:
            raise serializers.ValidationError(error, code='authorization')
        # correct_phone_number_if_valid(data, email_is_valid, number_is_valid)
        return data

    def save(self, request):
        cleaned_data = self.validated_data
        username = cleaned_data.get(USER_NAME_FIELD)

        adapter = get_adapter()
        user = adapter.new_user(request)
        user.username = username
        email_or_phone = "email" if self.username_is_email(username) else "phone"
        setattr(user, email_or_phone, username)
        user.save()

        if self.username_is_email(username):
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=False)
            send_email_verification_key(user)

            # setup_user_email(request, user, [])

        if 'password1' in cleaned_data:
            user.set_password(cleaned_data["password1"])
        else:
            user.set_unusable_password()

        user.save()
        return user


class AuthTokenSerializer(BaseAuthTokenSerializer, CustomValidationMixin):  # noqa
    username = serializers.CharField(
        label=_("Email or Phone"),
        error_messages={"required": _('Must include "phone/email"')}
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        error_messages={"required": _('Must include "password"')},
        trim_whitespace=False
    )
    code = serializers.CharField(required=True)
    google_assistant = serializers.BooleanField(default=False)

    def validate(self, attrs):
        username = attrs.get(USER_NAME_FIELD)
        try:
            username = get_validated_phone_number_with_code(attrs.get("code"), username) if not self.username_is_email(
                username) else username
        except NumberParseException:
                raise serializers.ValidationError(_(f"Invalid {username} Username."), code='invalid')

        attrs[USER_NAME_FIELD] = username

        password = attrs.get('password')

        error, email_is_valid, number_is_valid = self.perform_login_validations(attrs)

        if error:
            raise serializers.ValidationError(error, code='authorization')

        correct_phone_number_if_valid(attrs, email_is_valid, number_is_valid)

        username = attrs.get(USER_NAME_FIELD)
        password = attrs.get('password')

        user = authenticate(request=self.context.get('request'),
                            username=username, password=password)

        if not user:
            raise serializers.ValidationError(err_msg(msg="Unable to log in with provided credentials."),
                                              code='authorization')

        if email_is_valid:
            _object = EmailAddress.objects.filter(email__exact=username)
        else:
            _object = PhoneVerification.objects.filter(phone__exact=username)

        if _object.exists():
            _object = _object.first()
            google_assistant = attrs.get("google_assistant")
            if not _object.verified:
                error = err_msg(msg="Please Verify Your Account Before Login. OTP has been sent for email verification.")
                send_email_verification_key(user)
                raise serializers.ValidationError(error, code='authorization')
            if google_assistant and google_assistant == True:
                pass
            else:
                email_is_valid, number_is_valid = is_valid_email(username), is_valid_phone_number(username)
                if email_is_valid:
                    send_email_verification_key(user)
                elif number_is_valid:
                    recreate_new_user_key(user, username)
        else:
            # this case should not occur
            error = err_msg(msg="Incomplete account information. Account has not been created properly.")
            raise serializers.ValidationError(error, code='authorization')

        attrs['user'] = user

        return attrs


class PasswordResetTokenSerializer(EmailSerializer, CustomValidationMixin):  # noqa
    code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)  # we need to send field username from front-end for consistency
    email = serializers.HiddenField(required=False, default="")  # overriding super's field

    def validate(self, attrs):
        email_or_phone = attrs[USER_NAME_FIELD]

        error, email_is_valid, number_is_valid, = self.perform_login_validations(attrs)
        if error:
            raise serializers.ValidationError(error, code='authorization')

        users = User.objects.filter(username__iexact=email_or_phone)
        valid_users = [user for user in users if user.is_active and user.has_usable_password()]
        if not valid_users:
            msg = err_msg(msg="There is no active user associated to this email or username.")
            raise serializers.ValidationError(_(msg))

        return attrs


class CustomPasswordTokenSerializer(PasswordTokenSerializer):  # noqa

    def validate(self, attrs):
        password = attrs.get("password")
        token = attrs.get("token")

        password_reset_token_validation_time = get_password_reset_token_expiry_time()
        reset_password_token = ResetPasswordToken.objects.filter(key=token).first()
        if reset_password_token is None:
            raise serializers.ValidationError(err_msg("token", f"Incorrect OTP."))

        expiry_date = reset_password_token.created_at + timedelta(hours=password_reset_token_validation_time)
        if timezone.now() > expiry_date:
            reset_password_token.delete()
            raise serializers.ValidationError(err_msg("token", "Provided OTP is expired."))

        if not reset_password_token.user.has_usable_password():
            raise serializers.ValidationError(err_msg("password", "User password is not usable."))

        try:
            validate_password(
                password,
                user=reset_password_token.user,
                password_validators=get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
            )
        except ValidationError as e:
            raise serializers.ValidationError(err_msg(msg=e.messages))

        return attrs


def correct_phone_number_if_valid(data, email_is_valid, number_is_valid):
    if number_is_valid and not email_is_valid:
        phone_number = data[USER_NAME_FIELD]
        data[USER_NAME_FIELD] = get_validated_phone_number_with_code(data[REGION_CODE_FIELD], phone_number)


def err_msg(field="", msg=""):
    if field is None or field == "":
        return _(msg)
    return {field: [_(msg)]}
