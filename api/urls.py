# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

# Router para la Versión 1 (La estable)
router_v1 = DefaultRouter()
router_v1.register(r'encomiendas', views.EncomiendaViewSet, basename='encomienda')

# Router para la Versión 2 (Para futuros cambios)
router_v2 = DefaultRouter()
# Aquí registrarías tus futuros ViewSets de V2. Por ahora lo dejamos preparado.

urlpatterns = [
    # Autenticación y Documentación
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(), name='swagger'),
    
    # --- VERSIONAMIENTO ---
    # Exponemos las dos versiones en la misma API
    path('v1/', include(router_v1.urls)),
    path('v2/', include(router_v2.urls)),
]