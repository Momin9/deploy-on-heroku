from django.urls import path
from .views import *

urlpatterns = [
    path('rooms/', GetAllUsers.as_view(), name='rooms'),
    path('room/<str:room_name>/', ChatRoom.as_view(), name='room')
]
