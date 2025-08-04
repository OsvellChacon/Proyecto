from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from PIL import Image
from auditlog.registry import auditlog
from django.contrib.auth.models import User
import re
from usuarios.models import CustomUser

def validate_non_negative(value):
    if value < 0:
        raise ValidationError('Este campo no puede ser un número negativo.')

def validate_image_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError('La imagen no puede superar los 5 MB.')

def validate_image_dimensions(value):
    max_dimensions = (270, 270)
    image = Image.open(value)
    width, height = image.size
    if width > max_dimensions[0] or height > max_dimensions[1]:
        raise ValidationError('Las dimensiones de la imagen no pueden ser mayores a 270x270 píxeles.')


class Categorias(models.Model):
    nombre = models.CharField(max_length=20)
    portada = models.ImageField(
        upload_to='categorias/',  # <-- Cambiado aquí
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
            validate_image_dimensions,
        ]
    )

    def clean(self):
        if not re.match("^[A-Za-z]*$", self.nombre):
            raise ValidationError("El nombre solo puede contener letras.")

    def __str__(self):
        return self.nombre

class SubCategoria(models.Model):
    nombre = models.CharField(max_length=50)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='subcategorias')

    def __str__(self):
        return f'{self.categoria.nombre} - {self.nombre}'

class Unidades(models.Model):
    unidad = models.CharField(max_length=20)

    def clean(self):
        if not re.match("^[A-Za-z]*$", self.unidad):
            raise ValidationError("La unidad solo puede contener letras.")

    def __str__(self):
        return self.unidad

class UnidadesVenta(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

def validate_codigo(value):
    regex = r"^BOD-\d{4}$"
    if not re.match(regex, value):
        raise ValidationError('El código debe tener el formato BOD-0000.')

class Bodega(models.Model):
    codigo = models.CharField(max_length=20, unique=True, validators=[validate_codigo])
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'

class Stock(models.Model):
    producto = models.CharField(max_length=20)
    cantidad = models.IntegerField(validators=[validate_non_negative])
    unidad = models.ForeignKey(Unidades, on_delete=models.CASCADE)
    unidad_venta = models.ForeignKey(UnidadesVenta, on_delete=models.CASCADE, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative])
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    existencia_min = models.IntegerField(validators=[validate_non_negative])
    imagen = models.ImageField(
        upload_to='productos/',  # <-- Cambiado aquí
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
        ], blank=True, null=True
    )

    def __str__(self):
        return f'{self.producto} ({self.unidad_venta})'

    def vender_producto(self, cantidad):
        if cantidad > self.cantidad:
            raise ValidationError('No hay suficiente stock para realizar esta transacción.')
        else:
            self.cantidad -= cantidad
            self.save()

    def __str__(self):
        return self.producto

class PrecioPorUnidad(models.Model):
    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    unidad_venta = models.ForeignKey(UnidadesVenta, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_non_negative])

    def __str__(self):
        return f'{self.producto} - {self.unidad_venta} - {self.precio}'

class TransaccionInventario(models.Model):
    TIPOS_TRANSACCION = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=7, choices=TIPOS_TRANSACCION)
    cantidad = models.IntegerField(validators=[validate_non_negative])
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.tipo == 'SALIDA' and self.cantidad > self.producto.cantidad:
            raise ValidationError('No hay suficiente stock para realizar esta transacción.')
        elif self.tipo == 'SALIDA':
            self.producto.cantidad -= self.cantidad
        elif self.tipo == 'ENTRADA':
            self.producto.cantidad += self.cantidad
        self.producto.save()
        super(TransaccionInventario, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.producto} - {self.tipo} - {self.cantidad}'


class HistorialPrecio(models.Model):
    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.producto} - {self.precio_anterior} -> {self.precio_nuevo}'


class VariacionProducto(models.Model):
    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    nombre_variacion = models.CharField(max_length=50)
    valor = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.producto} - {self.nombre_variacion}: {self.valor}'


class StockBodega(models.Model):
    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[validate_non_negative])

    def __str__(self):
        return f'{self.producto} en {self.bodega}'


auditlog.register(Categorias)
auditlog.register(Unidades)
auditlog.register(Stock)
auditlog.register(TransaccionInventario)
auditlog.register(PrecioPorUnidad)
auditlog.register(StockBodega)
auditlog.register(HistorialPrecio)
