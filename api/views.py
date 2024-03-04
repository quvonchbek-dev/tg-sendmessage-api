import asyncio
import json
from collections import OrderedDict

from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView, Response, Request

from utils.functions import check_hash
from . import enums
from . import serializers
from .tgsession import TgSession

sessions = {}


class TestView(APIView):
    def post(self, request: Request):
        return Response({"status": "OK"})


class SendMessageView(APIView):
    @swagger_auto_schema(request_body=serializers.MessageSerializer)
    def post(self, request: Request):
        serializer = serializers.MessageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            status = enums.CustomStatusCodes.VALIDATION_ERROR
            return Response(dict(status=status.dict(), msgId=None))
        data: OrderedDict = serializer.validated_data
        ok = check_hash(data)
        if not ok:
            status = enums.CustomStatusCodes.INVALID_CREDENTIALS
            return Response(dict(status=status.dict(), msgId=None))

        status = enums.send_message(data)
        if isinstance(status, enums.CustomStatus):
            return Response(dict(status=status.dict(), msgId=None))

        return Response(status)


class AddTelegramAccount(APIView):
    @swagger_auto_schema(request_body=serializers.MessageSerializer)
    def post(self, request: Request):
        serializer = serializers.MessageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            status = enums.CustomStatusCodes.VALIDATION_ERROR
        data: OrderedDict = serializer.validated_data
        ok = check_hash(data)
        if not ok:
            status = enums.CustomStatusCodes.INVALID_CREDENTIALS
            return Response(dict(status=status.dict()))


# @swagger_auto_schema(request_body=serializers.SendCodeSerializer)
async def send_code_view(request: WSGIRequest):
    data = json.loads(request.body)
    serializer = serializers.SendCodeSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"error": "ValidationError"})
    try:
        data = serializer.validated_data
        phone = data.get("phone")
        account_name = data.get("account_name")
        if sessions.get(phone):
            try:
                del sessions[phone]
            except Exception as ex:
                return JsonResponse({"error": ex})
        tg_session = TgSession(account_name, phone)
        await tg_session.init()
        code_hash = await tg_session.send_code()
        sessions[phone] = tg_session
        return JsonResponse({"phone_code_hash": code_hash})
    except asyncio.CancelledError:
        return JsonResponse({"hello": "asyncio.CancelledError"})
    except Exception as ex:
        return JsonResponse(dict(error=str(ex)))


@swagger_auto_schema(request_body=serializers.CheckCodeSerializer)
async def check_code_view(request: WSGIRequest):
    serializer = serializers.CheckCodeSerializer()
    try:
        return JsonResponse({"hello": "CheckCodeSerializer"})
    except asyncio.CancelledError:
        raise


@swagger_auto_schema(request_body=serializers.CheckPasswordSerializer)
async def check_password_view(request: WSGIRequest):
    serializer = serializers.CheckPasswordSerializer()
    try:
        return JsonResponse({"hello": "CheckPasswordSerializer"})
    except asyncio.CancelledError:
        raise


# @api_view(http_method_names=['POST'])
async def resend_code_view(request: WSGIRequest):
    data = json.loads(request.body)
    serializer = serializers.ResendCodeRequestSerializer(data=data)
    if not serializer.is_valid():
        return JsonResponse({"error": "ValidationError"})
    try:
        data = serializer.validated_data
        phone = data.get("phone")
        account_name = data.get("account_name")
        if sessions.get(phone):
            try:
                del sessions[phone]
            except Exception as ex:
                return JsonResponse({"error": ex})
        tg_session = TgSession(account_name, phone)
        await tg_session.init()
        code_hash = await tg_session.send_code()
        sessions[phone] = tg_session
        return JsonResponse({"phone_code_hash": code_hash})
    except asyncio.CancelledError:
        return JsonResponse({"hello": "asyncio.CancelledError"})
    except Exception as ex:
        return JsonResponse(dict(error=str(ex)))


if __name__ == "__main__":
    pass
