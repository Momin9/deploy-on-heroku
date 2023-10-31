from Crypto.PublicKey import RSA
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from rest_framework.authtoken.models import Token

# from users.tasks import send_password_reset_email
from django.db.models.signals import post_save
from django.dispatch import receiver
# from django_rest_passwordreset.signals import reset_password_token_created
import uuid


class CaseInsensitiveQuerySet(QuerySet):
    def _filter_or_exclude(self, mapper, *args, **kwargs):
        for f in self.model.CASE_INSENSITIVE_FIELDS:
            if f in kwargs:
                kwargs[f + '__iexact'] = kwargs[f]
                del kwargs[f]
        return super(CaseInsensitiveQuerySet, self)._filter_or_exclude(mapper, *args, **kwargs)


def validate_password_strength(value):
    min_length = 8
    SpecialSym = ["$", "@", "#"]
    if len(value) < min_length:
        raise ValueError('Password must be at least {0} characters long.'.format(min_length))
    # check for 1 digits
    if not any(c.isdigit() for c in value):
        raise ValueError('Password must contain at least 1 digits.')
    # check for uppercase letter
    if not any(c.isupper() for c in value):
        raise ValueError('Password must contain at least 1 uppercase letter.')
        # check for lowercase letter
    if not any(c.islower() for c in value):
        raise ValueError('Password must contain at least 1 lowercase letter.')
    if not any(c in SpecialSym for c in value):
        raise ValueError('Password must contain at least 1 special character.You must from one of them $, @, #')
    return value


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        password = validate_password_strength(password)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        return user

    def get_queryset(self):
        return CaseInsensitiveQuerySet(self.model)


class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    phone = models.CharField(max_length=16, null=True, blank=True)
    public_key = models.TextField(null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)

    objects = MyUserManager()
    CASE_INSENSITIVE_FIELDS = ['email']
    USERNAME_FIELD = 'username' or 'email'

    def get_login_success_json(self):
        image_data = settings.SERVER_URL + '/media/' + str(self.userprofile.image)
        token, created = Token.objects.get_or_create(user=self)
        return {
            'user_id': self.pk,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'token': token.key,
            'image': image_data,
            'name': self.userprofile.name,
            'address': self.userprofile.address,
            'lng': self.userprofile.lng,
            'lat': self.userprofile.lat,
            'role': int(1)
        }

    def __str__(self):
        return str(self.username)


class UserProfile(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(max_length=512, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images', null=True, blank=True)
    lng = models.CharField(max_length=255, null=True, blank=True)
    lat = models.CharField(max_length=255, null=True, blank=True)


@receiver(post_save, sender=User)
@receiver(post_save, sender=User)
def build_profile_on_user_creation(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(owner=instance)
        profile.save()

        # RSA Encrypted Keys Generation
        key_pair = RSA.generate(1024)
        instance.public_key = key_pair.publickey().exportKey().decode()
        instance.private_key = key_pair.exportKey().decode()
        instance.save()


# @receiver(reset_password_token_created)
# def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
#     username = reset_password_token.user.username
#     email = reset_password_token.user.email
#     key = reset_password_token.key
#     send_password_reset_email(username, email, key)
