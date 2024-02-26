from django.contrib import admin
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import TestView, SendMessageView

schema_view = get_schema_view(
    openapi.Info(
        title="Telegram Userbot API",
        default_version='v1',
        description="Telegram userbot API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    # path('api-auth', include('rest_framework.urls')),
    # path('api/v1/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/v1/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/v1/test', TestView.as_view(), name="test_view"),
    path('api/v1/sendMessage', SendMessageView.as_view(), name="send_message")
]
