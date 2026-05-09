# envios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('encomiendas/', views.encomienda_list, name='encomienda_list'),
    path('encomiendas/<int:pk>/', views.encomienda_detail, name='encomienda_detail'),
    path('encomiendas/nueva/', views.encomienda_create, name='encomienda_create'),
]