from django.db import models
from usuarios.models import CustomUser

class Camiones(models.Model):
    conductor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="conductor")
    placa = models.CharField(max_length=15, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    year = models.IntegerField()
    capacidad_tanque = models.FloatField()
    gasolina_actual = models.FloatField(default=0)  # Nuevo campo
    
    def __str__(self):
        return f"{self.conductor} {self.placa} - {self.marca} {self.modelo}"

class UbicacionCamion(models.Model):
    camion = models.ForeignKey(Camiones, on_delete=models.CASCADE, related_name="locaciones")
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)
    ruta = models.JSONField(default=list)
    viaje_completado = models.BooleanField(default=False)  # Nuevo campo
    fecha_viaje = models.DateTimeField(auto_now_add=True)  # Nuevo campo
    gasolina_inicio = models.FloatField(default=0)  # Nuevo campo
    gasolina_fin = models.FloatField(default=0)     # Nuevo campo
    porcentaje_ahorrado = models.FloatField(default=0)  # Nuevo campo
    duracion_viaje = models.FloatField(default=0)  # Duración en minutos

    def __str__(self):
        return f"{self.camion.placa} - ({self.latitude}, {self.longitude})"
