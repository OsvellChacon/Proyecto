from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from inventario.models import *
from clientes.models import *
from usuarios.models import *
from clientes.views import *
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import redirect
from solicitudes.models import *
from django.http import JsonResponse
from django.core.serializers import serialize
from django.utils import timezone
# Create your views here.

@login_required
def dashboard(request):
    st = Stock.objects.all().count()
    cl = Tiendas.objects.all().count()
    total_usuarios = CustomUser.objects.count()
    
    facturas_recientes = Factura.objects.all().order_by('-fecha_creacion')[:10]
    
    # Formatear la fecha en el formato deseado con "am" o "pm"
    formatted_facturas_recientes = [{
      'fecha_creacion': timezone.localtime(factura.fecha_creacion).strftime("%m/%d/%Y %I:%M:%S %p"),
        'usuario': factura.usuario,
        'tienda': factura.tienda,
        'total': factura.total
    } for factura in facturas_recientes]

    facturas = Factura.objects.all()

    return render(request, "dashboard.html", {
        'st_counter': st,
        'chocolate': cl,
        'vanila': total_usuarios,
        'ordenes_recientes': formatted_facturas_recientes,
        'facturas': facturas,
        'page_title': 'Oseed | Dashboard'
    })

@login_required
def dashboard_json(request):
    st_count = Factura.objects.all().count()  # Número total de facturas
    tiendas_count = Factura.objects.values('tienda').distinct().count()  # Número total de tiendas con al menos una factura
    total_usuarios = Factura.objects.values('usuario').distinct().count()  # Número total de usuarios con al menos una factura
    
    # Obtener las 10 facturas más recientes
    facturas_recientes = Factura.objects.all().order_by('-fecha_creacion')[:10]
    
    # Formatear las facturas recientes en formato JSON
    formatted_facturas_recientes = [{
       'fecha_creacion': timezone.localtime(factura.fecha_creacion).strftime("%m/%d/%Y %I:%M:%S %p"),
        'usuario': factura.usuario.username,
        'tienda': factura.tienda.Cliente if factura.tienda else '',  
        'cliente': factura.cliente,
        'status': factura.status  # Aquí es donde se cambió a 'status'
    } for factura in facturas_recientes]

    # Crear un diccionario con los datos
    data = {
        'st_counter': st_count,
        'chocolate': tiendas_count,
        'vanila': total_usuarios,
        'ordenes_recientes': formatted_facturas_recientes,
    }

    # Devolver los datos en formato JSON
    return JsonResponse(data)

@login_required
def buscar(request):
    if 'q' in request.GET:
        query = request.GET['q']
        
        if not query:
            messages.error(request, 'Por favor, introduce un criterio de búsqueda.')
            return redirect('dashboard')
        
        try:
            # Intenta buscar un usuario por su nombre de usuario
            user = CustomUser.objects.get(username=query)
            return redirect('detalles_usuario', user_id=user.id)
        except CustomUser.DoesNotExist:
            pass

        try:
            # Intenta buscar un usuario por su nombre
            user = CustomUser.objects.get(nombre__icontains=query)
            return redirect('detalles_usuario', user_id=user.id)
        except CustomUser.DoesNotExist:
            pass

        try:
            # Intenta buscar un usuario por su cédula
            user = CustomUser.objects.get(cedula=query)
            return redirect('detalles_usuario', user_id=user.id)
        except CustomUser.DoesNotExist:
            pass

        try:
            # Intenta buscar un cliente por su nombre o apellido
            cliente = Clientes.objects.get(Nombre__icontains=query)
            return redirect('clientCard', id=cliente.id)
        except Clientes.DoesNotExist:
            pass

        try:
            # Intenta buscar una tienda por el nombre del cliente o por el RIF
            tienda = Tiendas.objects.filter(Cliente__icontains=query).first() or Tiendas.objects.get(RIF=query)
            return redirect('shopCard', id=tienda.id)
        except Tiendas.DoesNotExist:
            pass

        try:
            # Intenta buscar un producto por su ID
            producto_id = int(query)
            producto = Stock.objects.get(id=producto_id)
            return redirect('producto_transacciones', producto_id=producto.id)
        except (ValueError, Stock.DoesNotExist):
            pass

        try:
            # Intenta buscar un producto por su nombre
            producto = Stock.objects.filter(producto__icontains=query).first()
            if producto:
                return redirect('producto_transacciones', producto_id=producto.id)
            else: pass
        except Stock.DoesNotExist:
            messages.error(request, 'Error al buscar el producto.')

    return redirect('E404')

def error404(request): return render(request, "error-404.html")