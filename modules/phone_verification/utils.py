import random
import phonenumbers
from django.core.mail import send_mail

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from twilio.rest import Client

from users.utils import is_valid_email
from modules.phone_verification.models import PhoneVerificationKey, PhoneVerification
from smart_home_41612 import settings

User = get_user_model()


def send_message(number, message):
    try:
        from_ = settings.TWILIO_NUMBER
        client = Client(settings.TWILIO_ACCOUNT_ID, settings.TWILIO_AUTH_TOKEN)
        status = client.messages.create(body=message, to=number, from_=from_)
        return True
    except Exception as ex:
        return False


def send_email_verification_key(user):
    key = str(random.randint(1000, 9999))
    try:
        PhoneVerificationKey.objects.filter(user=user).delete()
        PhoneVerificationKey.objects.create(user=user, key=key)
        message = key + ' is your One Time Authentication PIN for email verification.' \
                        ' Please contact on info@enigma360.io or visit http://enigmatix.io for assistance.'
        html_message = render_to_string('otp/signup_email_otp_template.html', {'message': message})

        send_mail("OTP", message, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)
        return True
    except Exception as ex:
        return False


def create_new_user_key(user, key):
    PhoneVerification.objects.create(
        user=user, phone=user.phone
    )
    PhoneVerificationKey.objects.create(user=user, key=key)


def recreate_new_user_key(user, number):
    key = str(random.randint(100000, 999999))
    PhoneVerificationKey.objects.create(user=user, key=key)
    message = key + ' is your One Time Authentication PIN for Phone Number verification.' \
                    ' Please call 0334-2211313 or visit http://enigmatix.io for assistance.'
    return send_message(number, message)


def save_phone_verification(user, message, key):
    try:
        create_new_user_key(user, key)
    except Exception as e:
        return False
    return send_message(user.phone, message)


def send_verification_code(user):
    key = str(random.randint(100000, 999999))
    message = key + ' is your One Time Authentication PIN for Phone Number verification.' \
                    ' Please call 0334-2211313 or visit http://enigmatix.io for assistance.'
    return save_phone_verification(user, message, key)


def send_password_reset_token_phone(token_key, number):
    message = token_key + ' is your One Time Authentication PIN for Phone Number verification.' \
                          ' Please call 0334-2211313 or visit http://enigmatix.io for assistance.'
    return send_message(number, message)


def is_valid_phone_number(number):
    return True if number.startswith('+') and str(number[1:]).isnumeric() else number.isnumeric()


def get_validated_phone_number(phone):
    validate_phone = phonenumbers.parse(phone, None)
    country_code = validate_phone.country_code
    national_number = validate_phone.national_number
    number = '+' + str(country_code) + str(national_number)
    return number


def get_validated_phone_number_with_code(code, email_or_phone):
    if email_or_phone.startswith('+'):
        return get_validated_phone_number(email_or_phone)
    else:
        phone = '+' + code + email_or_phone
        return get_validated_phone_number(phone)


def is_email_or_phone(username):
    if is_valid_phone_number(username):
        return "phone"
    elif is_valid_email(username):
        return "email"
    return False
