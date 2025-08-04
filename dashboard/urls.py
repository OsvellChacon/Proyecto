from django.urls import path
from . import views
from usuarios.views import detalles_usuario
from inventario.views import main_stock

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path('buscar/', views.buscar, name='buscar'),
    path('usuarios/<int:user_id>/', detalles_usuario, name='detalles_usuario'),
    path("stock/", main_stock, name='inventario_general'),
    path('clientCard/<int:id>/', views.clienteCard, name='clienteCard'),
    path('shopCard/<int:id>/', views.shopCard, name='shopCard'),
        path('dashboard_json/', views.dashboard_json, name='dashboard_json'),
    path('error404/', views.error404, name='E404')
]