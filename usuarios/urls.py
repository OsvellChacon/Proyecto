from django.urls import path
from . import views

urlpatterns = [
    path("", views.usuarios, name='usuarios'),
    path('usuarios/', views.user_list, name='vista_usuarios'),
    path('create_user/', views.create_user, name='create_user'),
    path('update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user/<int:user_id>/', views.detalles_usuario, name='detalles_usuario'),
    path('user/<int:user_id>/asignar_permiso/<int:permission_id>/', views.asignar_permiso, name='asignar_permiso'),
    path('user/quitar_permiso/<int:user_id>/', views.quitar_permiso, name='quitar_permiso'),
    path('user/<int:user_id>/permissions/', views.view_user_permissions, name='view_user_permissions'),
    path('cargos/', views.ver_cargos, name='view_cargo'),
    path('create_cargo/', views.create_cargo, name='create_cargo'),
    path('update_cargo/<int:cargo_id>/', views.update_cargo, name='update_cargo'),
    path('delete_cargo/<int:cargo_id>/', views.delete_cargo, name='delete_cargo'),
    path('reporte_usuarios_pdf/', views.reporte_usuarios_pdf.as_view(), name='reporte_usuarios_pdf'),
    path('exportar_usuarios_excel/', views.exportar_usuarios_a_excel, name='exportar_usuarios_excel'),
]
