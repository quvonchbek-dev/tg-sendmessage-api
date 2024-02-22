from django.contrib.auth.models import User
from django.urls import path, include
from rest_framework import routers, serializers, viewsets


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=30)
    merchant_id = serializers.CharField(max_length=255)
    contact_name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True)
    # msg_type = serializers.ChoiceField(["text", "image", "audio", "video", "file"], default="text")
    message = serializers.CharField(max_length=None, min_length=None, allow_blank=True)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
