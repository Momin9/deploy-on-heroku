from django.urls import path, include
from rest_framework import routers
from users.views import (
    default_view,
    complete_view,
    AuthToken, ResetPasswordConfirm, ResetPasswordRequestToken, UserRegister, create_superuser, UserProfileViewSet

)

router = routers.DefaultRouter()

router.register(r'user/profile', UserProfileViewSet, basename='user_profile')

app_name = "users"
urlpatterns = [
    path('', include(router.urls)),
    path('', default_view),
    path('user/login/', AuthToken.as_view()),
    path('user/reset/confirm/', ResetPasswordConfirm.as_view(), name='password_confirm_reset'),
    path('user/password-reset/', ResetPasswordRequestToken.as_view()),
    path('registration/complete/', complete_view, name='account_confirm_complete'),
    path('user/register/', UserRegister.as_view()),
    path('superuser/create/', create_superuser, name='create_superuser'),
]
