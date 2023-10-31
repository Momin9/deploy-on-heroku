from django.contrib import admin
from .models import PhoneVerification, PhoneVerificationKey


class PhoneVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'phone', 'verified', 'created')
    readonly_fields = ['created']
    list_per_page = 50
    search_fields = ('user', 'phone', 'verified',)


class PhoneVerificationKeyAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'key', 'created')
    readonly_fields = ['created']
    list_per_page = 50
    search_fields = ('user', 'key',)


admin.site.register(PhoneVerification, PhoneVerificationAdmin)
admin.site.register(PhoneVerificationKey, PhoneVerificationKeyAdmin)
