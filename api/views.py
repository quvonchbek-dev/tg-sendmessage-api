from collections import OrderedDict

from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response, Request

from . import enums
from .serializers import MessageSerializer


class TestView(APIView):
    def post(self, request: Request):
        return Response({"status": "OK"})


class SendMessageView(APIView):
    # permission_classes = [IsAuthenticated]
    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request: Request):
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            status = enums.CustomStatusCodes.VALIDATION_ERROR
            return Response(dict(status=int(status), description=str(status), msg_id=None))
        data: OrderedDict = serializer.validated_data
        status, msg_id = enums.send_message(**data)
        status: enums.CustomStatus
        return Response(dict(status=int(status), description=str(status), msg_id=msg_id))
