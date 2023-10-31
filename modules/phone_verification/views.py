from datetime import timedelta

from allauth.account.models import EmailAddress
from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from chatapp.models import User
from todoproject import settings
from users.serializers import is_valid_email
from .utils import is_valid_phone_number, recreate_new_user_key, get_validated_phone_number_with_code, \
    send_email_verification_key
from .models import PhoneVerification, PhoneVerificationKey
from .serializers import VerifyPhoneNumberSerializer, CreateNewKeySerializer
from fcm_django.models import FCMDevice
from rest_framework.authtoken.models import Token


class CreateNewKeyViewSet(APIView):
    serializer_class = CreateNewKeySerializer
    permission_classes = (AllowAny,)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'username' and 'code' in request.data:
            username = request.data["username"]
            code = request.data['code']

            # Check if the provided username is a valid email address
            if is_valid_email(username):
                # If it's a valid email address, send an email OTP
                user = User.objects.filter(email__iexact=username).first()
                if user:
                    send_email_verification_key(user)  # Send email OTP
                    return Response({
                        'response': "Email OTP Sent",
                        "code": code, "username": username
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'response': ["Not a valid user."]}, status=status.HTTP_400_BAD_REQUEST)

            # Check if it's a valid phone number
            if is_valid_phone_number(username):
                number = get_validated_phone_number_with_code(code, username)
                if number:
                    phone_verify = PhoneVerification.objects.filter(phone__exact=number)
                    if phone_verify.exists():
                        phone_verify_obj = phone_verify.get(phone__exact=number)
                        user = phone_verify_obj.user
                        phone_key_obj = PhoneVerificationKey.objects.filter(user=user).first()
                        if phone_key_obj is None:
                            recreate_new_user_key(user, number)
                        else:
                            phone_key_obj.delete()
                            recreate_new_user_key(user, number)
                        send_email_verification_key(user)  # Send email OTP
                        return Response({
                            'response': "Verification Codes Sent",
                            "code": code, "username": username
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({'response': ["Not a valid user."]}, status=status.HTTP_400_BAD_REQUEST)

            # If neither email nor phone number, return an error
            response = ["Not a valid number or email address"]
            return Response({"response": response}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'response': ["Please Provide Required Data."]}, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneNumber(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyPhoneNumberSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        now_time = timezone.now()

        if 'key' and 'username' and 'code' in request.data:
            username = request.data["username"]
            device_id = request.data["deviceId"]
            code = request.data['code']
            check_email_or_phone = is_valid_email(username)
            key = request.data["key"]
            if check_email_or_phone:
                email_verify = EmailAddress.objects.filter(email__exact=username).first()
                phone_key_obj = PhoneVerificationKey.objects.filter(key=key).first()
                if phone_key_obj is None:
                    content = "Incorrect OTP."
                    return Response({'response': content}, status=status.HTTP_404_NOT_FOUND)

                key_created = phone_key_obj.created
                expiry_date = key_created + timedelta(minutes=settings.TWILIO_VERIFY_KEY_EXPIRY_MINUTES)
                if now_time > expiry_date:
                    phone_key_obj.delete()
                    content = 'OTP Expired, Please Request Again.'
                    return Response({'status': content}, status=status.HTTP_404_NOT_FOUND)
                if phone_key_obj:
                    email_verify.verified = True
                email_verify.save()
                if key == phone_key_obj.key:
                    phone_key_obj.delete()

                if email_verify.verified:
                    role = 1
                    user = email_verify.user
                    token, created = Token.objects.get_or_create(user=user)
                    image_data = settings.SERVER_URL + '/media/' + str(user.userprofile.image)
                    return Response({
                        'token': token.key,
                        'user_id': user.pk,
                        'email': user.email,
                        'username': user.username,
                        'image': image_data,
                        'name': user.userprofile.name,
                        'address': user.userprofile.address,
                        'phone': user.phone,
                        'lng': user.userprofile.lng,
                        'lat': user.userprofile.lat,
                        'role': int(role)
                    })
                return Response({
                    'error_phone': 'Please Verify Your Account Before Login.'
                }, status=status.HTTP_404_NOT_FOUND)
                # response = "Not a Valid Number"
                # return Response({"response": response}, status=status.HTTP_400_BAD_REQUEST)
            if is_valid_phone_number(username):
                number = get_validated_phone_number_with_code(code, username)
            else:
                return Response({'response': 'Please provide valid number.'})
            if number:
                phone_verify = PhoneVerification.objects.filter(phone__exact=number)
                if phone_verify.exists():
                    phone_verify_obj = phone_verify.get(phone__exact=number)
                    phone_key_obj = PhoneVerificationKey.objects.filter(key=key).first()
                    if phone_key_obj is None:
                        content = "No OTP Found. Please Request Again."
                        return Response({'response': content}, status=status.HTTP_404_NOT_FOUND)
                    key_created = phone_key_obj.created
                    expiry_date = key_created + timedelta(minutes=settings.TWILIO_VERIFY_KEY_EXPIRY_MINUTES)
                    if now_time > expiry_date:
                        phone_key_obj.delete()
                        content = 'OTP Expired, Please Request Again.'
                        return Response({'status': content}, status=status.HTTP_404_NOT_FOUND)
                    if key == phone_key_obj.key:
                        phone_verify_obj.verified = True
                        phone_verify_obj.save()
                        if device_id != 0:
                            try:
                                num = "+" + code + username[1:]
                                device = FCMDevice.objects.filter(user__username=num).first()
                                if device is not None:
                                    if device.device_id != device_id:
                                        title = "Security alert"
                                        description = "Trying to signin from new device? we recommend you review your recent activity"
                                        device.send_message(title, description)
                            except:
                                print("no data found")
                        else:
                            print("device id none")
                        phone_key_obj.delete()
                    phone_verify = PhoneVerification.objects.filter(phone__exact=number)
                    if phone_verify.exists():
                        phone_verify_obj = phone_verify.first()
                        if phone_verify_obj.verified:
                            role = 1
                            user = phone_verify_obj.user
                            token, created = Token.objects.get_or_create(user=user)
                            image_data = settings.SERVER_URL + '/media/' + str(user.userprofile.image)
                            return Response({
                                'token': token.key,
                                'user_id': user.pk,
                                'email': user.email,
                                'username': user.username,
                                'image': image_data,
                                'name': user.userprofile.name,
                                'address': user.userprofile.address,
                                'phone': user.phone,
                                'lng': user.userprofile.lng,
                                'lat': user.userprofile.lat,
                                'role': int(role)
                            })
                        return Response({
                            'error_phone': 'Please Verify Your Account Before Login.'
                        }, status=status.HTTP_404_NOT_FOUND)
                    return Response({
                        'error_phone': 'You need to Create an Account.'
                    }, status=status.HTTP_404_NOT_FOUND)
                    # return Response({'response': "Verified"}, status=status.HTTP_200_OK)
                return Response({'response': "Not a valid user."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'response': "Please Provide Required Data."}, status=status.HTTP_400_BAD_REQUEST)
