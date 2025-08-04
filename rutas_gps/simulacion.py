import random
import time
from django.utils.timezone import now
from models import Camiones, UbicacionCamion

# Coordenadas aproximadas de Venezuela
VENEZUELA_BOUNDS = {
    "lat_min": 0.6, "lat_max": 12.2,
    "lon_min": -73.4, "lon_max": -59.8
}

def generar_coordenadas():
    """Genera una ubicación aleatoria en Venezuela."""
    lat = random.uniform(VENEZUELA_BOUNDS["lat_min"], VENEZUELA_BOUNDS["lat_max"])
    lon = random.uniform(VENEZUELA_BOUNDS["lon_min"], VENEZUELA_BOUNDS["lon_max"])
    return lat, lon

def mover_camiones():
    """Simula el movimiento de los camiones."""
    camiones = Camiones.objects.all()
    for camion in camiones:
        # Obtener última ubicación
        ultima_ubicacion = UbicacionCamion.objects.filter(camion=camion).order_by('-timestamp').first()
        
        if ultima_ubicacion:
            # Pequeño cambio en la ubicación para simular movimiento
            nueva_lat = ultima_ubicacion.latitude + random.uniform(-0.05, 0.05)
            nueva_lon = ultima_ubicacion.longitude + random.uniform(-0.05, 0.05)
        else:
            # Si no tiene ubicación previa, generar una inicial
            nueva_lat, nueva_lon = generar_coordenadas()

        # Guardar nueva ubicación
        UbicacionCamion.objects.create(camion=camion, latitude=nueva_lat, longitude=nueva_lon)
        print(f"Camión {camion.placa} movido a ({nueva_lat}, {nueva_lon})")

# Bucle infinito para actualizar cada 5 segundos
if __name__ == "__main__":
    while True:
        mover_camiones()
        time.sleep(5)
