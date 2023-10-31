from rest_framework import serializers


class VerifyPhoneNumberSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    key = serializers.CharField(required=True)
    deviceId = serializers.CharField(required=False)

    class Meta:
        fields = '__all__'


class CreateNewKeySerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        fields = '__all__'
