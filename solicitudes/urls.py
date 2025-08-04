from django.urls import path
from . import views

urlpatterns = [
    path("", views.solicitudes, name="solicitudes"),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('eliminar_producto_carrito/<int:producto_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('vaciar_carrito/', views.vaciar_carrito, name='vaciar_carrito'),
    path('actualizar_cantidad_producto/', views.actualizar_cantidad_producto, name='actualizar_cantidad_producto'),
    path('confirmar-compra/', views.confirmar_compra, name='confirmar_compra'),
    path('ver_facturas/', views.ver_facturas, name='ver_facturas'),
    path('eliminar_factura/<int:factura_id>/', views.eliminar_factura, name='eliminar_factura'),
    path('ver_facturas_usuario/', views.ver_facturas_usuario, name='ver_facturas_usuario'),  
    path('cambiar_estado_factura/', views.cambiar_estado_factura, name='cambiar_estado_factura'),
]
