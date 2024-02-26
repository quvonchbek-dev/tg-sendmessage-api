from rest_framework import serializers


class MessageSerializer(serializers.Serializer):
    chatId = serializers.CharField(max_length=30, allow_blank=True, allow_null=True, default="")
    merchantId = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=30, allow_blank=True, allow_null=True, default="")
    username = serializers.CharField(max_length=100, allow_blank=True, allow_null=True, default="")
    photo = serializers.CharField(max_length=255, allow_blank=True, allow_null=True, default="")
    firstName = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, default="Firstname")
    lastName = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, default="Lastname")
    message = serializers.CharField(max_length=None, min_length=1, required=True)
    timestamp = serializers.IntegerField()
    hash = serializers.CharField(max_length=255)
