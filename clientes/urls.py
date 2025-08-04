from django.urls import path
from . import views

urlpatterns = [
    path("", views.cliente, name='cliente'),
    path('ver_clientes/', views.viewClients, name='Clientes'),
    path('tiendas/', views.Shops, name='Tiendas'),
    path('clientCard/<id>/', views.clienteCard, name='clientCard'),
    path('shopCard/<id>/', views.shopCard, name='shopCard'),
    path('agregartiendas/', views.addShop, name='AddShoping'),
    path('acttiendas/<id>/', views.updateStore, name='uptShoping'),
    path('dlttiendas/<id>/', views.deleteStore, name='dltShoping'),
    path('agregarCliente/', views.addClient, name='AddClient'),
    path('actCliente/<id>/', views.updateClient, name='uptClient'),
    path('dltCliente/<id>/', views.deleteClient, name='dltClient'),
    
    path('reporte_tiendas_to_pdf/', views.reporte_tiendas.as_view(), name='tiendaPDF'),
    path('export_tiendas_to_excel/', views.export_tiendas_to_excel, name='tiendaExcel'),
    path('reporte_clientes_to_pdf/', views.reporte_clientes.as_view(), name='clientesPDF'),
    path('export_clientes_to_excel/', views.export_clientes_to_excel, name='clientesExcel'),
    path('importarExcel/', views.importarExcel, name='importarExcel'),
]