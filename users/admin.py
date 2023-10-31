from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import UserProfile

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password', 'phone')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('RSA Encryption Keys'), {'fields': ('public_key', 'private_key')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name',)
    ordering = ('username',)
    list_per_page = 50
    date_hierarchy = 'date_joined'
    list_filter = ['is_superuser', 'is_staff', 'is_active']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileAdmin(admin.ModelAdmin):
    form = UserProfileForm
    list_display = ('owner', 'name')
    list_per_page = 50

    search_fields = ('name',)


admin.site.register(UserProfile, UserProfileAdmin)
