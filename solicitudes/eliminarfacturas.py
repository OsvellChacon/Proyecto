from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import Factura

@require_POST
def eliminar_factura(request, factura_id):
    factura = get_object_or_404(Factura, pk=factura_id)
    factura.delete()
    return JsonResponse({'message': 'Factura eliminada correctamente'})
