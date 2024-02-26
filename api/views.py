from collections import OrderedDict

from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView, Response, Request

from utils.functions import check_hash
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


if __name__ == "__main__":
    pass
