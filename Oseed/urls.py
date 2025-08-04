"""
URL configuration for Oseed project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls'), name='Home'),
    path('', views.login_view, name='login'),
    path('dashboard/', include('dashboard.urls'), name='dashboard'),
    path('inventario/', include('inventario.urls'), name='inventario'),
    path('clientes/', include('clientes.urls'), name='clientes'),
    path('solicitudes/', include('solicitudes.urls'), name='solicitudes'),
    path('usuarios/', include('usuarios.urls'), name='usuarios'),
    path('rutas_gps/', include('rutas_gps.urls'), name='rutas_gps'),
    path('auditoria/', include('auditoria.urls'), name='auditoria'),
    path('select2/', include('django_select2.urls')),
    path('cerrar_sesion/', views.cerrar_sesion, name='logout')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)