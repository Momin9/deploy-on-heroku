from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid
User = get_user_model()


class PhoneVerification(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    user = models.ForeignKey(User,
                             verbose_name=_('user'),
                             on_delete=models.CASCADE)
    phone = models.CharField(unique=True,
                             max_length=20,
                             verbose_name=_('phone number'))
    verified = models.BooleanField(verbose_name=_('verified'), default=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("phone number")
        verbose_name_plural = _("phone numbers")
        unique_together = [("user", "phone")]

    def __str__(self):
        return self.phone


class PhoneVerificationKey(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)

    key = models.CharField(verbose_name=_('key'), max_length=64)
    user = models.ForeignKey(User,
                             verbose_name=_('user'),
                             on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("Verify Key")
        verbose_name_plural = _("Verify Keys")
        unique_together = [("user", "key")]
