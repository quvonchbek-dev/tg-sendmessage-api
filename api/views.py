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
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=MessageSerializer)
    def post(self, request: Request):
        serializer = MessageSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(dict(status=False, msg="Message object format is invalid"))
        data: OrderedDict = serializer.validated_data
        msg_id = res = enums.send_message(**data)
        status, error = True, None
        if not isinstance(res, int):
            status = False
            error = res
            msg_id = None
        return Response(dict(status=status, error=error, msg_id=msg_id))
