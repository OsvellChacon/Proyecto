from django.core.mail import send_mail
from django.db import models, transaction
from django.contrib.auth import get_user_model
from inventario.models import Stock
from clientes.models import Tiendas
from django.contrib import messages
from usuarios.models import CustomUser
from django.core.validators import MinValueValidator

class Factura(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    cliente = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=False)
    tienda = models.ForeignKey(Tiendas, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_creacion} - ${self.total}"

class Carrito(models.Model):
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    producto = models.ForeignKey(Stock, on_delete=models.CASCADE)
    cantidad = models.IntegerField(validators=[MinValueValidator(0)])  
    total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.total = self.cantidad * self.producto.precio
        super().save(*args, **kwargs)

    def completar_orden(self):
        with transaction.atomic():
            if self.producto.cantidad >= self.cantidad:
                self.producto.cantidad -= self.cantidad
                self.producto.save()

                factura = Factura(
                    usuario=self.usuario,
                    total=self.total,
                    cliente=self.usuario.get_full_name(),
                    tienda=self.producto.tienda  
                )
                factura.save()

                messages.success(self.usuario, f'Tu orden para {self.producto.producto} se ha completado con éxito. Se ha generado una factura.')

                subject = 'Orden completada con éxito'
                message = f'Tu orden para {self.producto.producto} se ha completado con éxito. Se ha generado una factura.'
                from_email = 'carlos.osvell@gmail.com'
                recipient_list = [self.usuario.email]

                send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                return True
            else:
                messages.warning(self.usuario, f'Lo sentimos, no hay suficiente stock para {self.cantidad} unidades de {self.producto.producto}. Revise la cantidad en su carrito.')
                return False
