from django.db import models
from django.core.exceptions import ValidationError
import re
from auditlog.registry import auditlog

# Función para validar el RIF
def validar_rif(value):
    if not value[0].isupper():
        raise ValidationError("El RIF debe comenzar con una letra mayúscula.")

    regex = r"^[A-Z]-\d{8}-\d$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El RIF no tiene el formato correcto.")

# Modelo Tiendas
class Tiendas(models.Model):
    Cliente = models.CharField(max_length=100)
    RIF = models.CharField(max_length=12, unique=True, validators=[validar_rif])
    Direccion = models.TextField()
    Status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.Cliente

    def get_status_display(self):
        return "Activo" if self.Status else "Inactivo"

    def get_badge_class(self):
        return "success" if self.Status else "danger"

    def resumen(self):
        return f"{self.Cliente} | RIF: {self.RIF} | Dirección: {self.Direccion} | Estatus: {self.get_status_display()}"

# Validación de nombre
def validar_nombre(value):
    regex = r"^[a-zA-Z ]+$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El nombre no tiene el formato correcto.")

def validar_cedula(value):
    regex = r"^(\d{2}\.\d{3}\.\d{3}|\d{1}\.\d{3}\.\d{3})$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("La cédula no tiene el formato correcto. Debe ser 'XX.XXX.XXX' o 'X.XXX.XXX'.")

# Validación de correo electrónico
def validar_correo(value):
    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El correo no tiene el formato correcto.")

# Validación de teléfono
def validar_telefono(value):
    regex = r"^\+\d{1,4}\d{9,}$"  # + seguido de 1 a 4 dígitos y luego 9 o más dígitos adicionales
    pattern = re.compile(regex)
    if not pattern.match(value):
        raise ValidationError("El teléfono no tiene el formato correcto. Debe empezar con '+' seguido de al menos 10 dígitos.")

# Modelo Clientes
class Clientes(models.Model):
    Nombre = models.CharField(max_length=20, validators=[validar_nombre])
    Apellido = models.CharField(max_length=20, validators=[validar_nombre])
    Cedula = models.CharField(max_length=12, unique=True, validators=[validar_cedula])
    Correo = models.EmailField(unique=True, validators=[validar_correo])
    Telefono = models.CharField(max_length=15, validators=[validar_telefono])
    Tienda = models.ForeignKey(Tiendas, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.Nombre} {self.Apellido}"

# Auditorías para la aplicación "Clientes"
auditlog.register(Clientes)
auditlog.register(Tiendas)
