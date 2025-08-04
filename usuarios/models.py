from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from PIL import Image
import re
from auditlog.registry import auditlog

# Validación para el peso máximo de la imagen (2 MB)
def validate_image_size(value):
    max_size = 2 * 1024 * 1024  # 2 MB en bytes
    if value.size > max_size:
        raise ValidationError(_('El tamaño de la imagen no puede exceder los 2 MB.'))

class Cargos(models.Model):
    Nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.Nombre

def validar_nombre(value):
    regex = r"^[a-zA-Z ]+$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El nombre no tiene el formato correcto.")

def validar_cedula(value):
    regex = r"^\d{2}\.\d{3}\.\d{3}$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("La cédula no tiene el formato correcto.")

def validar_correo(value):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El correo no tiene el formato correcto.")

def validar_telefono(value):
    regex = r"^\+\d{1,4}\d{9,}$"  # + seguido de 1 a 4 dígitos y luego 9 o más dígitos adicionales
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El teléfono no tiene el formato correcto. Debe empezar con algun prefijo '+58' seguido del número.")

class CustomUser(AbstractUser):
    nombre = models.CharField(max_length=100, validators=[validar_nombre])
    apellido = models.CharField(max_length=100, validators=[validar_nombre])
    cedula = models.CharField(max_length=20, validators=[validar_cedula])
    direccion = models.TextField()
    telefono = models.CharField(max_length=15, validators=[validar_telefono])
    cargo = models.ForeignKey(Cargos, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(unique=True)
    imagen_perfil = models.ImageField(upload_to='perfil/', default='perfil/default.jpg', validators=[validate_image_size])
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre + " " + self.apellido

auditlog.register(CustomUser)