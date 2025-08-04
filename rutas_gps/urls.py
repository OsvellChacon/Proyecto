from django.urls import path
from . import views

urlpatterns = [
    path('', views.mapa, name='mapa'),  # Vista principal para mostrar el mapa
    path('ubicaciones/', views.ubicaciones_camiones, name='ubicaciones_camiones'),
    path('calcular_duracion', views.calcular_duracion, name='calcular_duracion'),
    path('guardar_ruta', views.guardar_ruta, name='guardar_ruta'),# Vista principal para mostrar el mapa# Vista para obtener las ubicaciones en formato JSON
    path('vehiculos/', views.vehiculos_list, name='vista_vehiculos'),
    path('vehiculos/crear/', views.crearVehiculos, name='crear_vehiculo'),
    path('vehiculos/<int:user_id>/', views.detalles_vehiculos, name='detalles_vehiculo'),
    path('vehiculos/<int:user_id>/editar/', views.update_vehiculo, name='editar_vehiculo'),
    path('vehiculos/<int:user_id>/eliminar/', views.delete_vehiculo, name='eliminar_vehiculo'),
    path('vehiculos/<int:user_id>/exportar_excel/', views.exportar_historial_excel, name='exportar_historial_excel'),
    path('viaje/<int:viaje_id>/ruta/', views.obtener_ruta_viaje, name='obtener_ruta_viaje'),
    path('viaje/<int:viaje_id>/ver_mapa/', views.ver_mapa_ruta, name='ver_mapa_ruta'),
]
