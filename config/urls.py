# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Panel de Administración de Django
    path('admin/', admin.site.urls),
    
    # Rutas de Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # --- RUTAS ESPECÍFICAS PRIMERO ---
    path('api/', include('api.urls')), 
    
    # --- RUTA RAÍZ AL FINAL ---
    path('', include('envios.urls')),
]