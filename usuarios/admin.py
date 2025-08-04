from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Cargos

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('username', 'nombre', 'apellido', 'cedula', 'telefono', 'email', 'cargo', 'is_staff')
    search_fields = ('username', 'nombre', 'apellido', 'email', 'cedula', 'telefono')
    readonly_fields = ('date_joined', 'last_login')

    # Campos adicionales al editar usuarios
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': (
                'nombre',
                'apellido',
                'cedula',
                'telefono',
                'direccion',
                'cargo',
                'imagen_perfil',
            )
        }),
    )

    # Campos adicionales al crear usuarios
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': (
                'nombre',
                'apellido',
                'cedula',
                'telefono',
                'direccion',
                'cargo',
                'imagen_perfil',
            )
        }),
    )

@admin.register(Cargos)
class CargosAdmin(admin.ModelAdmin):
    list_display = ('Nombre',)
    search_fields = ('Nombre',)
