from rest_framework.permissions import BasePermission
from chatapp.permissions import SAFE_METHODS_DEVICE
from users.models import UserProfile

SAFE_METHODS_DEVICE_STATUS = ['GET', 'PUT', 'PATCH', 'OPTIONS']


class IsOwnerProfile(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS_DEVICE:
            user = request.user
            owner = UserProfile.objects.filter(owner__exact=user)
            if owner:
                return True
            return False
        return False
