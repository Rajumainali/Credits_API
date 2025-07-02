from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views  

schema_view = get_schema_view(
    openapi.Info(
        title="Credit Keeper API",
        default_version='v1',
        description="API for managing buyer credits and purchases",
        contact=openapi.Contact(email="your-email@example.com"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/', include('credit_app.urls')),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),

    #Add Django's default login view for Swagger UI
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
