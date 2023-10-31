import re
from django.contrib.auth import get_user_model

from modules.phone_verification.models import PhoneVerificationKey

User = get_user_model()


regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


def is_valid_email(email):
    """ :returns: True if provided email is valid else False."""
    return True if re.search(regex, email) else False


def user_already_registered(email_or_phone):
    existing_email = User.objects.filter(username__exact=email_or_phone)
    return existing_email.exists()


def clear_expired_keys(expiry_time):
    PhoneVerificationKey.objects.filter(created__lte=expiry_time).delete()
