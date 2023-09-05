from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer, RegisterSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view


# Class based view to Get User Details using Token Authentication
class UserDetailAPI(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


# Class based view to register user
class RegisterUserAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['POST'])
def create_superuser(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_superuser(username=username, password=password, email=email)
    return Response({'success': 'Superuser created', "user": user}, status=status.HTTP_201_CREATED)
