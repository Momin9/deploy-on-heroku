from django.contrib import admin
from django import forms

from chatapp.models import *


# Register your models here.
class MessageAdminForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'


class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    list_display = ('sender_user', 'receiver_user', 'timestamp', 'message')
    readonly_fields = ['created', 'last_updated', ]
    list_per_page = 1000
    search_fields = ('sender_user', 'receiver_user', 'timestamp', 'message',)


class RoomAdminForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = '__all__'


class RoomAdmin(admin.ModelAdmin):
    form = RoomAdminForm
    list_display = ('sender_user', 'receiver_user', 'room_name')
    readonly_fields = ['created', 'last_updated', ]
    list_per_page = 1000
    search_fields = ('sender_user', 'receiver_user', 'room_name',)


admin.site.register(Message, MessageAdmin)
admin.site.register(Room, RoomAdmin)
