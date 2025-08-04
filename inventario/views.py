from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import View
from .utils import render_to_pdf
import pandas as pd
from reportlab.pdfgen import canvas
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
@permission_required('inventario.view_stock')
def inventario(request):
    st = Stock.objects.all().count()
    ct = Categorias.objects.all()
    
    categorias_y_totales = []

    for categoria in ct:
        total_productos = Stock.objects.filter(categoria=categoria).count()
        categorias_y_totales.append((categoria, total_productos))
        
    sukuna = {
        'stock': st, 
        'cat_total': categorias_y_totales,
        'page_title': 'Oseed | Gestion de Inventario'
    }
    
    return render(request, "inventario.html", sukuna)

@login_required
@permission_required('inventario.view_categorias')
def view_categorias(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    productos = Stock.objects.filter(categoria=categoria)

    page = request.GET.get('page', 1)

    paginator = Paginator(productos, 5)

    try:
        productos = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        productos = paginator.page(paginator.num_pages)
        
    Nanami = {
        'categoria': categoria,
        'productos': productos,
        'paginator': paginator,
        'page_title': f'Oseed | Categoria: {categoria.nombre}'
    }

    return render(request, "categoria.html", Nanami)

@login_required
@permission_required('inventario.view_stock')
def main_stock(request):
    query = request.GET.get('q', '')
    st = Stock.objects.all()

    if query:
        st = st.filter(Q(producto__icontains=query))
        if not st.exists():
            messages.info(request, "El producto buscado no se encuentra en existencia, por favor verifique e intente de nuevo.")
    else:
        st = st.order_by('-id')

    # Paginación
    page = request.GET.get('page', 1)

    paginator = Paginator(st, 5)

    try:
        st = paginator.page(page)
    except (EmptyPage, PageNotAnInteger):
        st = paginator.page(paginator.num_pages)

    # Obtener transacciones por producto
    for producto in st:
        producto.transacciones = producto.transaccioninventario_set.all()
        
    context = {
        'stock': st, 
        'paginator': paginator,
        'page_title': 'Oseed | Inventario General'
    }

    return render(request, "stock.html", context)

@login_required
@permission_required('inventario.view_stock')
def producto_transacciones(request, producto_id):
    producto = get_object_or_404(Stock, id=producto_id)
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Por favor, proporciona las fechas en el formato YYYY-MM-DD.')
            return render(request, "producto_transacciones.html", {'producto': producto})

        transacciones = producto.transaccioninventario_set.filter(fecha__range=(fecha_inicio, fecha_fin)).order_by('-fecha')[:2]
    else:
        transacciones = producto.transaccioninventario_set.all().order_by('-fecha')[:2]
        if 'fecha_inicio' in request.GET or 'fecha_fin' in request.GET:
            messages.error(request, 'Por favor, proporciona ambas fechas.')

    Toji = {
        'producto': producto, 
        'transacciones': transacciones,
        'page_title': f'Oseed | Historial: {producto.producto}'
    }

    return render(request, "producto_transacciones.html", Toji)

class ReporteTransacciones(View):
    def get(self, request, producto_id, *args, **kwargs):
        producto = get_object_or_404(Stock, id=producto_id)
        fecha_inicio = request.GET.get('fecha_inicio')
        fecha_fin = request.GET.get('fecha_fin')

        if fecha_inicio and fecha_fin:
            transacciones = producto.transaccioninventario_set.filter(Q(fecha__gte=fecha_inicio) & Q(fecha__lte=fecha_fin)).order_by('-id')
        else:
            transacciones = producto.transaccioninventario_set.all().order_by('-id')
            if 'fecha_inicio' in request.GET or 'fecha_fin' in request.GET:
                messages.error(request, 'Por favor, proporciona ambas fechas.')

        data = {
            'producto': producto,
            'transacciones': transacciones
        }
        
        pdf = render_to_pdf("reporte_transacciones.html", data)
        filename = "reporte_transaccion_" + producto.producto + ".pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
        return response

@login_required
@permission_required('inventario.add_stock')
def addProducts(request):
    if request.method == 'POST':
        form = StockFrm(request.POST, request.FILES)

        if form.is_valid():
            # Guardar el producto
            form.save()

            messages.success(request, 'Producto Agregado Con Éxito')
            return redirect('inventario_general')
        else:
            messages.error(request, 'Hubo un error al agregar el producto. Asegúrate de que todos los campos sean válidos.')

    else:
        form = StockFrm()

    context = {
        'form': form,
        'page_title': 'Oseed | Agregar Producto'
    }
    return render(request, "addProductos.html", context)

@login_required
@permission_required('inventario.change_stock')
def updateProduct(request, id):
    producto = get_object_or_404(Stock, id=id)

    if request.method == 'POST':
        form = StockActFrm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado con éxito')
            return redirect('inventario_general')
        else:
            messages.error(request, 'Hubo un error al actualizar el producto. Por favor verifica los datos proporcionados.')
    else:
        form = StockActFrm(instance=producto)

    context = {
        'form': form,
        'page_title': f'Oseed | {producto.producto}'
    }
    
    return render(request, "updateProducto.html", context)

@login_required
@permission_required('inventario.delete_stock')
def eliminarProducto(request, id):
    producto = get_object_or_404(Stock, id=id)
    producto.delete()
    messages.success(request, "Producto Eliminado Con Exito")
    return redirect('inventario_general')

# Reportes
class reporte_stock(View):
    def get(self, request, *args, **kwargs):
        template_name = "reporteStock.html"
        reporte = Stock.objects.all()
        data = {
            'entity': reporte
        }
        pdf = render_to_pdf(template_name, data)
        return HttpResponse(pdf, content_type='application/pdf')

@login_required
@permission_required('inventario.view_stock')
def export_stock_to_excel(request):
    stocks = Stock.objects.all().select_related('categoria', 'unidad')

    data = [{
        'producto': s.producto,
        'cantidad': s.cantidad,
        'unidad': s.unidad.unidad,  
        'precio': s.precio,
        'categoria': s.categoria.nombre 
    } for s in stocks]

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=stock.xlsx'

    df.to_excel(response, index=False)

    return response

class generar_reporte_pdf(View):
    def get(self, request, id, *args, **kwargs):
        categoria = get_object_or_404(Categorias, id=id)
        productos = Stock.objects.filter(categoria=categoria)

        filename = "reporte_" + categoria.nombre + ".pdf"

        data = {
            'categoria': categoria,
            'productos': productos
        }

        pdf = render_to_pdf("reporteProductos.html", data)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

        return response

@login_required
@permission_required('inventario.view_stock')
def generar_reporte_excel(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    productos = Stock.objects.filter(categoria=categoria).select_related('unidad')

    data = [{
        'producto': p.producto,
        'cantidad': p.cantidad,
        'unidad': p.unidad.unidad,
        'precio': p.precio,
    } for p in productos]

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    return response

@login_required
@permission_required('inventario.add_categorias')
def agregarCategoria(request):
    if request.method == 'POST':
        form = CategoriaFrm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría agregada con éxito')
            return redirect('inventario')
        else:
            messages.error(request, 'Hubo un error al agregar la categoría. Asegúrate de que todos los campos sean válidos.')

    else:
        form = CategoriaFrm()

    context = {
        'form': form,
        'page_title': 'Oseed | Agregar Categoria'
    }
    
    return render(request, "categorias.html", context)

@login_required
@permission_required('inventario.change_categorias')
def updateCategoria(request, id):
    categoria = get_object_or_404(Categorias, id=id)

    if request.method == 'POST':
        form = CategoriaFrm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada con éxito')
            return redirect('inventario')
        else:
            messages.error(request, 'Hubo un error al actualizar la categoría. Verifica los datos proporcionados.')

    else:
        form = CategoriaFrm(instance=categoria)

    context = {
        'form': form,
        'page_title': f'Oseed | Categoria: {categoria.nombre}'
    }
    
    return render(request, "updateCategoria.html", context)

@login_required
@permission_required('inventario.delete_categorias')
def eliminarCategoria(request, id):
    categoria = get_object_or_404(Categorias, id=id)
    categoria.delete()
    messages.success(request, "Categoria Eliminada Con Exito")
    return redirect('inventario')

@login_required
@permission_required('inventario.view_stock')
def agregarUnidad(request):
    maomao = Unidades.objects.all()
    
    for unidad in maomao:
        unidad.productos_count = Stock.objects.filter(unidad=unidad).count()
    
    page = request.GET.get('page', 1)
    paginator = Paginator(maomao, 5)

    try:
        maomao = paginator.page(page)
    except PageNotAnInteger:
        maomao = paginator.page(1)
    except EmptyPage:
        maomao = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = UnidadesFrm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidad Agregada Con Exito')
            return redirect('addUnidad')
    else:
        form = UnidadesFrm()

    data = {
        'form': form,
        'unidad': maomao,
        'paginator': paginator,
        'page_title': 'Oseed | Gestionar Unidades'
    }

    return render(request, 'unidades.html', data)

@login_required
@permission_required('inventario.change_unidades')
def updateUnidad(request, id):
    unidad = get_object_or_404(Unidades, id=id)

    if request.method == 'POST':
        form = UnidadesFrm(request.POST, request.FILES, instance=unidad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unidad actualizada con éxito')
            return redirect('addUnidad')
        else:
            messages.error(request, 'Hubo un error al actualizar la unidad. Verifica los datos proporcionados.')

    else:
        form = UnidadesFrm(instance=unidad)

    context = {
        'form': form,
        'page_title': f'Oseed | Unidad: {unidad.unidad}'
    }
    return render(request, "updateUnidad.html", context)

@login_required
@permission_required('inventario.delete_unidades')
def eliminarUnidad(request, id):
    unidad = get_object_or_404(Unidades, id=id)
    unidad.delete()
    messages.success(request, "Unidad Eliminada Con Exito")
    return redirect('addUnidad')

# Bodegas
@login_required
@permission_required('inventario.view_bodega')
def bodegas(request):
    query = request.GET.get('q')
    if query:
        bodegas_list = Bodega.objects.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        ).order_by('codigo')
    else:
        bodegas_list = Bodega.objects.all().order_by('codigo')
        
    page = request.GET.get('page', 1)
    paginator = Paginator(bodegas_list, 5)  # Muestra 5 usuarios por página

    try:
        bodegas_list = paginator.page(page)
    except PageNotAnInteger:
        bodegas_list = paginator.page(1)
    except EmptyPage:
        bodegas_list = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'Oseed | Gestionar Bodegas',
        'bodegas': bodegas_list,
        'query': query,
        'paginator': paginator
    }

    return render(request, "bodegas/bodega.html", context)

@login_required
@permission_required('inventario.view_bodega')
def verBodegas(request, id):
    
    Cruela = get_object_or_404(Bodega, id=id)
    Odra = StockBodega.objects.all()
    
    for producto in Odra:
        producto.productos_count = StockBodega.objects.filter(producto=producto).count()
    
    Toji = {
        'page_title': 'Oseed | Bodega',
        'producto': Odra,
        'Bodegas': Cruela
    }
    
    return render(request, "bodegas/verBodega.html", Toji)

@login_required
@permission_required('inventario.add_bodega')
def agregar_bodega(request):
    if request.method == 'POST':
        form = BodegaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bodega agregada con éxito.')
            return redirect('bodegas')
    else:
        form = BodegaForm()
        
    Yuta = {
        'form': form,
        'page_title': 'Oseed | Agregar Bodega'
    }

    return render(request, 'bodegas/agregar_bodega.html', Yuta)

@login_required
@permission_required('inventario.change_bodega')
def actualizar_bodega(request, id):
    bodega = get_object_or_404(Bodega, id=id)

    if request.method == 'POST':
        form = BodegaForm(request.POST, instance=bodega)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bodega actualizada con éxito.')
            return redirect('bodegas')
        else:
            messages.error(request, 'Hubo un error al actualizar la bodega. Verifica los datos proporcionados.')
    else:
        form = BodegaForm(instance=bodega)
        
    Maki = {
        'form': form,
        'page_title': f'Oseed | ({bodega.nombre} - {bodega.codigo})'
    } 

    return render(request, 'bodegas/actualizar_bodega.html', Maki)

@login_required
@permission_required('inventario.delete_bodega')
def eliminar_bodega(request, id):
    bodega = get_object_or_404(Bodega, id=id)
    bodega.delete()
    messages.success(request, 'Bodega eliminada con éxito')
    return redirect('bodegas')

# SubCategorías
@login_required
@permission_required('inventario.view_subcategoria')
def listar_subcategorias(request):
    subcategorias = SubCategoria.objects.all().order_by('nombre')
    return render(request, "subcategorias.html", {'subcategorias': subcategorias})

@login_required
@permission_required('inventario.add_subcategoria')
def agregar_subcategoria(request):
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoría agregada con éxito.')
            return redirect('listar_subcategorias')
    else:
        form = SubCategoriaForm()
    return render(request, 'agregar_subcategoria.html', {'form': form})

@login_required
@permission_required('inventario.change_subcategoria')
def actualizar_subcategoria(request, id):
    subcategoria = get_object_or_404(SubCategoria, id=id)
    if request.method == 'POST':
        form = SubCategoriaForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcategoría actualizada con éxito.')
            return redirect('listar_subcategorias')
        else:
            messages.error(request, 'Hubo un error al actualizar la subcategoría. Verifica los datos proporcionados.')
    else:
        form = SubCategoriaForm(instance=subcategoria)
    return render(request, 'actualizar_subcategoria.html', {'form': form})

@login_required
@permission_required('inventario.delete_subcategoria')
def eliminar_subcategoria(request, id):
    subcategoria = get_object_or_404(SubCategoria, id=id)
    if request.method == 'POST':
        subcategoria.delete()
        messages.success(request, 'Subcategoría eliminada con éxito.')
        return redirect('listar_subcategorias')
    return render(request, 'confirmar_eliminar_subcategoria.html', {'subcategoria': subcategoria})

# Precios Por Unidad
@login_required
@permission_required('inventario.view_precio_por_unidad')
def agregar_precio_por_unidad(request):
    precios = PrecioPorUnidad.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(precios, 5)

    try:
        precios = paginator.page(page)
    except PageNotAnInteger:
        precios = paginator.page(1)
    except EmptyPage:
        precios = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = PrecioPorUnidadFrm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Precio agregado con éxito.')
            return redirect('add_precio_por_unidad')
    else:
        form = PrecioPorUnidadFrm()

    data = {
        'form': form,
        'precios': precios,
        'paginator': paginator
    }

    return render(request, 'precio_por_unidad.html', data)

@login_required
@permission_required('inventario.change_precioporunidad')
def actualizar_precio_por_unidad(request, id):
    precio = get_object_or_404(PrecioPorUnidad, id=id)
    if request.method == 'POST':
        form = PrecioPorUnidadFrm(request.POST, instance=precio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Precio actualizado con éxito.')
            return redirect('add_precio_por_unidad')
        else:
            messages.error(request, 'Hubo un error al actualizar el precio. Verifica los datos proporcionados.')
    else:
        form = PrecioPorUnidadFrm(instance=precio)

    data = {
        'form': form
    }

    return render(request, 'update_precio_por_unidad.html', data)

@login_required
@permission_required('inventario.delete_precioporunidad')
def eliminar_precio_por_unidad(request, id):
    precio = get_object_or_404(PrecioPorUnidad, id=id)
    if request.method == 'POST':
        precio.delete()
        messages.success(request, "Precio eliminado con éxito.")
        return redirect('add_precio_por_unidad')
    return render(request, 'confirmar_eliminar_precio.html', {'precio': precio})

# Historial de Precio
@login_required
@permission_required('inventario.view_historialprecio')
def agregar_historial_precio(request):
    historial = HistorialPrecio.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(historial, 5)

    try:
        historial = paginator.page(page)
    except PageNotAnInteger:
        historial = paginator.page(1)
    except EmptyPage:
        historial = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = HistorialPrecioFrm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Historial de precio agregado con éxito.')
            return redirect('add_historial_precio')
    else:
        form = HistorialPrecioFrm()

    data = {
        'form': form,
        'historial': historial,
        'paginator': paginator
    }

    return render(request, 'historial_precio.html', data)

@login_required
@permission_required('inventario.change_historialprecio')
def actualizar_historial_precio(request, id):
    historial = get_object_or_404(HistorialPrecio, id=id)
    if request.method == 'POST':
        form = HistorialPrecioFrm(request.POST, instance=historial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Historial de precio actualizado con éxito.')
            return redirect('add_historial_precio')
        else:
            messages.error(request, 'Hubo un error al actualizar el historial. Verifica los datos proporcionados.')
    else:
        form = HistorialPrecioFrm(instance=historial)

    data = {
        'form': form
    }

    return render(request, 'update_historial_precio.html', data)

@login_required
@permission_required('inventario.delete_historialprecio')
def eliminar_historial_precio(request, id):
    historial = get_object_or_404(HistorialPrecio, id=id)
    if request.method == 'POST':
        historial.delete()
        messages.success(request, "Historial de precio eliminado con éxito.")
        return redirect('add_historial_precio')
    return render(request, 'confirmar_eliminar_historial.html', {'historial': historial})

# Variación Producto
@login_required
@permission_required('inventario.view_variacionproducto')
def agregar_variacion_producto(request):
    variaciones = VariacionProducto.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(variaciones, 5)

    try:
        variaciones = paginator.page(page)
    except PageNotAnInteger:
        variaciones = paginator.page(1)
    except EmptyPage:
        variaciones = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = VariacionProductoFrm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variación de producto agregada con éxito.')
            return redirect('add_variacion_producto')
    else:
        form = VariacionProductoFrm()

    data = {
        'form': form,
        'variaciones': variaciones,
        'paginator': paginator
    }

    return render(request, 'variacion_producto.html', data)

@login_required
@permission_required('inventario.change_variacionproducto')
def actualizar_variacion_producto(request, id):
    variacion = get_object_or_404(VariacionProducto, id=id)
    if request.method == 'POST':
        form = VariacionProductoFrm(request.POST, instance=variacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Variación de producto actualizada con éxito.')
            return redirect('add_variacion_producto')
        else:
            messages.error(request, 'Hubo un error al actualizar la variación. Verifica los datos proporcionados.')
    else:
        form = VariacionProductoFrm(instance=variacion)

    data = {
        'form': form
    }

    return render(request, 'update_variacion_producto.html', data)

@login_required
@permission_required('inventario.delete_variacionproducto')
def eliminar_variacion_producto(request, id):
    variacion = get_object_or_404(VariacionProducto, id=id)
    if request.method == 'POST':
        variacion.delete()
        messages.success(request, "Variación de producto eliminada con éxito.")
        return redirect('add_variacion_producto')
    return render(request, 'confirmar_eliminar_variacion.html', {'variacion': variacion})

# Stock Bodega
@login_required
@permission_required('inventario.view_stockbodega')
def agregar_stock_bodega(request):
    stock = StockBodega.objects.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(stock, 5)

    try:
        stock = paginator.page(page)
    except PageNotAnInteger:
        stock = paginator.page(1)
    except EmptyPage:
        stock = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = StockBodegaFrm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock de bodega agregado con éxito.')
            return redirect('add_stock_bodega')
    else:
        form = StockBodegaFrm()

    data = {
        'form': form,
        'stock': stock,
        'paginator': paginator
    }

    return render(request, 'stock_bodega.html', data)

@login_required
@permission_required('inventario.change_stockbodega')
def actualizar_stock_bodega(request, id):
    stock = get_object_or_404(StockBodega, id=id)
    if request.method == 'POST':
        form = StockBodegaFrm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock de bodega actualizado con éxito.')
            return redirect('add_stock_bodega')
        else:
            messages.error(request, 'Hubo un error al actualizar el stock. Verifica los datos proporcionados.')
    else:
        form = StockBodegaFrm(instance=stock)

    data = {
        'form': form
    }

    return render(request, 'update_stock_bodega.html', data)