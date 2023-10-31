import uuid

from rest_framework.permissions import BasePermission, SAFE_METHODS
from home.models import Services, Components


class IsOwnerProfileOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


SAFE_METHODS_DEVICE = ['GET']


def is_valid_uuid(key):
    try:
        val = uuid.UUID(str(key), version=4)
    except:
        return False
    return True


class IsAccessKey(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS_DEVICE:
            key = request.query_params.get('key')
            val = is_valid_uuid(key)
            if val:
                service_obj = Services.objects.filter(device__access_key__exact=key)
                if service_obj:
                    if request.headers["User-Agent"] == 'ESP8266HTTPClient':
                        return True
                    return False
                return False
            return False
        return False


SAFE_METHODS_DEVICE_STATUS = ['GET']


class IsAccessDevice(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS_DEVICE:
            device_name = request.query_params.get('device_name')
            if device_name:
                device_obj = Services.objects.filter(device__device_name__exact=device_name)
                if device_obj:
                    if request.headers["User-Agent"] == 'ESP8266HTTPClient':
                        return True
                    return False
                return False
            return False
        return False

