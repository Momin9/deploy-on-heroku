from django.urls import path
from .views import *


urlpatterns = [
    path('api/v1/phone-verify/', VerifyPhoneNumber.as_view()),
    path('api/v1/phone-resend/', CreateNewKeyViewSet.as_view()),

]
