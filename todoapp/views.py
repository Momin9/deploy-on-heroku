# from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
# from rest_framework.views import APIView
# from rest_framework.response import Response
#
# from .models import Tasks
# from .serializers import UserSerializer, RegisterSerializer, TasksSerializer
# from rest_framework import generics, viewsets
# from django.contrib.auth.models import User
# from rest_framework import status
# from rest_framework.decorators import api_view
#
#
# class UserDetailAPI(APIView):
#     permission_classes = (IsAuthenticated,)
#     serializer_classe = UserSerializer
#
#     def get(self, request, *args, **kwargs):
#         user = User.objects.get(id=request.user.id)
#         serializer = UserSerializer(user)
#         return Response(serializer.data)
#
#
# class RegisterUserAPIView(generics.CreateAPIView):
#     permission_classes = (AllowAny,)
#     serializer_class = RegisterSerializer
#
#
# class TaskViewSet(viewsets.ModelViewSet):
#     queryset = Tasks.objects.all()
#     serializer_class = TasksSerializer
#
#     def create(self, request, *args, **kwargs):
#         # Your custom logic for task creation
#         # For example, you can implement business rules or additional validation
#         # Check if the user has the required permissions
#
#         if not request.user.has_perm('your_app.add_task'):
#             return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
#
#         # Deserialize the request data using the serializer
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # Perform your custom logic here
#         # For instance, set the owner of the task to the current user
#         task = serializer.save(owner=request.user)
#
#         # You can perform additional actions here, like sending notifications or triggering other processes
#
#         # Serialize the task and return it in the response
#         return Response(TasksSerializer(task).data, status=status.HTTP_201_CREATED)
#
#
# @api_view(['POST'])
# def create_superuser(request):
#     username = request.data.get('username')
#     password = request.data.get('password')
#     email = request.data.get('email')
#
#     if not username or not password or not email:
#         return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
#
#     user = User.objects.create_superuser(username=username, password=password, email=email)
#     return Response({'success': 'Superuser created', "user": user}, status=status.HTTP_201_CREATED)
