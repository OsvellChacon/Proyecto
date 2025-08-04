from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from inventario.models import *
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import *
from django.core.exceptions import ValidationError
from .models import Carrito
from inventario.models import Stock, Categorias
from .models import Factura
from .forms import FacturaForm
from django.contrib.auth.decorators import user_passes_test


def solicitudes(request):
    stocks = Stock.objects.all().order_by('-id')
    cat = Categorias.objects.all().order_by('nombre')
    selected_category_id = request.GET.get('category_id')

    if selected_category_id:
        stocks = stocks.filter(categoria_id=selected_category_id)
        
    return render(request, "solicitudes.html", {
        'categorias': cat,
        'productos': stocks,
        'selected_category_id': selected_category_id,
    })

@login_required
def agregar_al_carrito(request, producto_id):
    if not request.user.is_authenticated:
        messages.warning(request, 'AVISO! Debes iniciar sesión para agregar productos al carrito.')
        return redirect('solicitudes')

    producto = get_object_or_404(Stock, id=producto_id)

    if producto.cantidad < 1:
        messages.warning(request, 'Este producto no está disponible actualmente.')
        return redirect('solicitudes')

    usuario = request.user

    # Intentar obtener el producto del carrito del usuario
    try:
        carrito_item = Carrito.objects.get(usuario=usuario, producto=producto)
    except Carrito.DoesNotExist:
        # Si no existe, crea un nuevo registro en el carrito
        carrito_item = Carrito(usuario=usuario, producto=producto, cantidad=0, total=0)

    # Incrementar la cantidad del producto en el carrito
    carrito_item.cantidad += 1
    carrito_item.total += producto.precio
    carrito_item.save()

    # Actualizar el stock del producto
    try:
        with transaction.atomic():
            producto.vender_producto(1)
            messages.success(request, 'Stock actualizado.')
    except ValidationError as e:
        messages.warning(request, str(e))

    # Redireccionar a la página de solicitudes
    return redirect('solicitudes')

@login_required
def obtener_total_carrito(request):
    # Aquí es donde obtienes el total del carrito
    usuario = request.user
    total_carrito = sum(item.total for item in Carrito.objects.filter(usuario=usuario))
    
    # Devuelve los datos en formato JSON
    return JsonResponse({'total_carrito': total_carrito})

@login_required
def ver_carrito(request):
    usuario = request.user
    carrito = Carrito.objects.filter(usuario=usuario)
    total_carrito = sum(item.total for item in carrito)

    factura_form = FacturaForm()

    if request.method == 'POST':
        factura_form = FacturaForm(request.POST)

        if factura_form.is_valid():
            # Procesar el formulario de confirmación de compra
            factura = factura_form.save(commit=False)
            factura.usuario = usuario
            factura.total = total_carrito

            # Asociar los elementos del carrito a la factura
            for item in carrito:
                item.factura = factura
                item.save()

            # Limpiar el carrito después de completar la compra
            Carrito.objects.filter(usuario=usuario).delete()

            # Guardar la factura después de asociar los elementos del carrito y limpiarlo
            factura.save()

            messages.success(request, '¡Compra completada con éxito!')

            return redirect('ver_carrito')

    fecha_y_hora_actual = timezone.now()
    fecha_y_hora_actual_formateada = fecha_y_hora_actual.strftime('%Y-%m-%d %H:%M:%S')

    return render(request, 'carrito.html', {
        'carrito': carrito,
        'total_carrito': total_carrito,
        'fecha_y_hora_actual_formateada': fecha_y_hora_actual_formateada,
        'factura_form': factura_form,
    })

@login_required
def eliminar_producto_carrito(request, producto_id):
    usuario = request.user
    producto = get_object_or_404(Stock, id=producto_id)

    if Carrito.objects.filter(usuario=usuario, producto=producto).exists():
        carrito_item = Carrito.objects.get(usuario=usuario, producto=producto)
        carrito_item.delete()
        messages.success(request, 'Producto eliminado del carrito.')
    else:
        messages.warning(request, 'El producto no está en tu carrito.')

    return redirect('ver_carrito')

@login_required
def vaciar_carrito(request):
    usuario = request.user

    Carrito.objects.filter(usuario=usuario).delete()
    messages.success(request, 'Carrito vaciado correctamente.')

    return redirect('ver_carrito')

@require_POST
def actualizar_cantidad_producto(request):
    producto_id = request.POST.get('producto_id')
    nueva_cantidad = request.POST.get('nueva_cantidad')

    producto = get_object_or_404(Stock, id=producto_id)
    
    try:
        producto.cantidad = nueva_cantidad
        producto.save()
        return JsonResponse({'mensaje': 'Cantidad actualizada correctamente'})
    except Exception as e:
        return JsonResponse({'mensaje': str(e)}, status=500)
    
@login_required
def confirmar_compra(request):
    usuario = request.user
    carrito = Carrito.objects.filter(usuario=usuario)
    total_carrito = sum(item.total for item in carrito)

    # Verificar si el carrito está vacío
    if not carrito.exists():
        messages.error(request, 'Tu carrito está vacío. Añade productos antes de confirmar la compra.')
        return redirect('ver_carrito')

    if request.method == 'POST':
        factura_form = FacturaForm(request.POST)

        if factura_form.is_valid():
            with transaction.atomic():
                factura = factura_form.save(commit=False)
                factura.usuario = usuario
                factura.total = total_carrito
                factura.save()

                for item in carrito:
                    item.factura = factura
                    item.save()

                    transaccion = TransaccionInventario(
                        producto=item.producto,
                        tipo='SALIDA',  # Como es una compra, estamos sacando productos del inventario
                        cantidad=item.cantidad,
                    )
                    transaccion.save()

                # Limpiar el carrito después de completar la compra
                Carrito.objects.filter(usuario=usuario).delete()
                messages.success(request, '¡Transacción realizada! Tu compra ha sido confirmada.')

                return redirect('dashboard')  # Redirigir al usuario al dashboard

    else:
        factura_form = FacturaForm()

    return render(request, 'confirmar_compra.html', {'carrito': carrito, 'total_carrito': total_carrito, 'factura_form': factura_form})

@login_required
def ver_facturas(request):
    if request.method == 'POST' and request.is_ajax():
        factura_id = request.POST.get('factura_id')
        nuevo_estado = request.POST.get('status')

        try:
            factura = Factura.objects.get(id=factura_id)
            factura.status = nuevo_estado
            factura.save()
            return JsonResponse({'success': True})
        except Factura.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'La factura no existe'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    facturas = Factura.objects.all().order_by('-id')
    
    fecha = request.GET.get('fecha')
    if fecha:
        facturas = facturas.filter(fecha_creacion=fecha)
        
    usuario = request.GET.get('usuario')
    if usuario:
        facturas = facturas.filter(usuario__username=usuario)
        
    for factura in facturas:
        elementos_carrito = Carrito.objects.filter(factura=factura)
        productos_factura = [elemento_carrito.producto for elemento_carrito in elementos_carrito]
        factura.productos = productos_factura

    return render(request, 'ver_facturas.html', {'facturas': facturas})

@login_required
@require_POST
def cambiar_estado_factura(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        factura_id = request.POST.get('factura_id')
        nuevo_estado = request.POST.get('status')

        try:
            factura = Factura.objects.get(id=factura_id)
            factura.status = nuevo_estado
            factura.save()
            return JsonResponse({'success': True})
        except Factura.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'La factura no existe'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'La solicitud no es AJAX o no es POST'})

@login_required
def ver_facturas_usuario(request):
    usuario = request.user
    facturas = Factura.objects.filter(usuario=usuario).order_by('-fecha_creacion')
    
    return render(request, 'ver_facturas.html', {'facturas': facturas})

@login_required
def imprimir_factura(request, factura_id):
    factura = get_object_or_404(Factura,id=factura_id)
    return render(request, 'ver_facturas.html', {'factura': factura})

@require_POST
def eliminar_factura(request, factura_id):
    factura = get_object_or_404(Factura, pk=factura_id)
    factura.delete()
    return JsonResponse({'message': 'Factura eliminada correctamente'})

@login_required
def obtener_carrito_json(request):
    usuario = request.user
    carrito = Carrito.objects.filter(usuario=usuario)
    carrito_data = []

    for item in carrito:
        producto_data = {
            'id': item.producto.id,
            'nombre': item.producto.nombre,
            'precio': item.producto.precio,
            'cantidad': item.cantidad,
            'total': item.total,
        }
        carrito_data.append(producto_data)

    total_carrito = sum(item.total for item in carrito)

    return JsonResponse({'carrito': carrito_data, 'total_carrito': total_carrito})

def actualizar_precio_total(request):
    if request.method == 'POST' and request.is_ajax():
        precio_total = request.POST.get('precio_total')
        
        # Aquí puedes procesar el precio total del carrito como desees
        # Por ejemplo, puedes almacenarlo en la sesión del usuario, en la base de datos, etc.
        
        # Por ahora, simplemente responderemos con un mensaje JSON indicando que el precio total se recibió correctamente
        return JsonResponse({'mensaje': 'Precio total del carrito recibido correctamente.'})
    else:
        # Si la solicitud no es POST o no es una solicitud AJAX, devolvemos un error 400 (Bad Request)
        return JsonResponse({'error': 'La solicitud debe ser POST y AJAX.'}, status=400)
    
def actualizar_cantidad_producto(request):
    if request.method == 'POST' and request.is_ajax():
        producto_id = request.POST.get('producto_id')
        nueva_cantidad = request.POST.get('nueva_cantidad')

        # Actualizar la cantidad del producto en el carrito en la base de datos
        # Código para actualizar el carrito
        # ...

        return JsonResponse({'mensaje': 'Cantidad actualizada correctamente'})
    else:
        return JsonResponse({'error': 'La solicitud debe ser POST y AJAX.'}, status=400)
    