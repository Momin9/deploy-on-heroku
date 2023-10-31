from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import SET
from django.db.models.signals import post_save

User = get_user_model()


class BulkCreateManager(models.Manager):
    def bulk_create(self, objs, **kwargs):
        for item in objs:
            post_save.send(item.__class__, instance=item, created=True)
        return super().bulk_create(objs, **kwargs)


class CommonFields(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Message(CommonFields):
    """
    model for storing the message of the chat
    """
    sender_user = models.ForeignKey(User, on_delete=SET(AnonymousUser.id), related_name='sent_messages')
    receiver_user = models.ForeignKey(User, on_delete=SET(AnonymousUser.id), related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_user} to {self.receiver_user}: {self.message}"


class Room(CommonFields):
    """
    model for chat rooms
    """
    sender_user = models.ForeignKey(User, on_delete=SET(AnonymousUser.id), related_name='room_sender')
    receiver_user = models.ForeignKey(User, on_delete=SET(AnonymousUser.id), related_name='room_receiver')
    room_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.room_name
