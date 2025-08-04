from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Categorias)
admin.site.register(SubCategoria)
admin.site.register(Unidades)
admin.site.register(UnidadesVenta)
admin.site.register(Stock)
admin.site.register(Bodega)
admin.site.register(PrecioPorUnidad)
admin.site.register(TransaccionInventario)
admin.site.register(HistorialPrecio)
admin.site.register(VariacionProducto)
admin.site.register(StockBodega)