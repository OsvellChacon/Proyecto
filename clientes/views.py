from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.views.generic import View
from .utils import render_to_pdf
import pandas as pd
from reportlab.pdfgen import canvas
from django.http import Http404, JsonResponse, HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from datetime import datetime

# Create your views here.
@login_required
@permission_required('clientes.view_clientes')
def cliente(request):
    num_total = Tiendas.objects.count()
    Suguru = Clientes.objects.count()
    
    Gojo = Tiendas.objects.all().order_by('-id')[:5]
    
    if not Gojo.exists():
        messages.error(request, "No se encontraron tiendas recientes.")
    
    context = {
        'num_total': num_total, 
        'Satoru': Suguru,
        'tiendas': Gojo,
        'page_title': 'Oseed | Clientes'
    }
    
    return render(request, "clientes.html", context)

@login_required
@permission_required('clientes.view_clientes')
def viewClients(request):
    query = request.GET.get('q', '')
    if query:
        satoru = Clientes.objects.filter(Q(Nombre__icontains=query) | Q(Apellido__icontains=query) | Q(Cedula__icontains=query)).order_by('-id')
    else:
        satoru = Clientes.objects.all().order_by('-id')

    if not satoru.exists():
        messages.error(request, "No se encontró ningún cliente con ese nombre, apellido o número de cédula.")
        
    context = {
        'cliente': satoru,
        'page_title': 'Oseed | Gestion de Clientes'
    }

    return render(request, 'vistaClientes.html', context)

@login_required
@permission_required('clientes.view_tiendas')
def Shops(request):
    query = request.GET.get('q', '')
    shop = Tiendas.objects.filter(Q(Cliente__icontains=query) | Q(RIF__icontains=query)).order_by('-id')
    if not shop.exists():
        messages.error(request, "No se encontró ninguna tienda con ese nombre o RIF.")

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(shop, 5)
        shop = paginator.page(page)
    except:
        raise Http404
    
    context = {
        'shop': shop, 
        'paginator': paginator,
        'page_title': 'Oseed | Gestion de Tiendas'
    }

    return render(request, 'Tiendas.html', context)

@login_required
@permission_required('clientes.view_clientes')
def clienteCard(request, id):
    cliente = get_object_or_404(Clientes, id=id)
    
    context = {
        'cliente': cliente,
        'page_title': f'Oseed | {cliente.Nombre} {cliente.Apellido}'
        }
    
    return render(request, "clientecard.html", context)

@login_required
@permission_required('clientes.view_tiendas')
def shopCard(request, id):
    cliente = get_object_or_404(Tiendas, id=id)
    
    context = {
        'cliente': cliente,
        'page_title': f'Oseed | {cliente.Cliente}'
    }
    
    return render(request, "shopcard.html", context)

@login_required
@permission_required('clientes.add_tiendas')
def addShop(request):
    if request.method == 'POST':
        s = TiendaFrm(request.POST)
        if s.is_valid():
            try:
                s.save()
                messages.success(request, 'Tienda Agregada Con Exito')
                return redirect('Tiendas')
            except IntegrityError:
                messages.error(request, 'Ya existe una tienda con ese RIF.')
    else:
        s = TiendaFrm()

    context = {
        'shop': s,
        'page_title': 'Oseed | Agregar Tienda'
    }
    return render(request, "AddStore.html", context)

@login_required
@permission_required('clientes.change_tiendas')
def updateStore(request, id):
    p = Tiendas.objects.get(id=id)

    if request.method == 'POST':
        form = TiendaFrm(request.POST, instance=p)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Tienda actualizada con éxito')
                return redirect('Tiendas')
            except IntegrityError:
                messages.error(request, 'Ya existe una tienda con ese RIF.')
    else:
        form = TiendaFrm(instance=p)

    context = {
        'shop': form,
        'page_title': f'Oseed | {p.Cliente}'
    }
    return render(request, "UptStore.html", context)

@login_required
@permission_required('clientes.delete_tiendas')
def deleteStore(request, id):
    p = get_object_or_404(Tiendas, id=id)
    p.delete()
    messages.success(request, "Tienda Eliminada con Exito")
    return redirect('Tiendas')

class reporte_tiendas(View):
    def get(self, request, *args, **kwargs):
        template_name = "reporteTiendas.html"
        reporte = Tiendas.objects.all().order_by('-id')
        data = {
            'entity': reporte
        }
        pdf = render_to_pdf(template_name, data)
        return HttpResponse(pdf, content_type='application/pdf')

@login_required
@permission_required('clientes.view_tiendas')
def export_tiendas_to_excel(request):
    tiendas = Tiendas.objects.all().order_by('-id')

    data = [{
        'Cliente': t.Cliente,
        'RIF': t.RIF,
        'Direccion': t.Direccion
    } for t in tiendas]

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=tiendas.xlsx'

    df.to_excel(response, index=False)

    return response

@login_required
@permission_required('clientes.view_tiendas')
def importarExcel(request):
    if request.method == 'POST':
        try:
            excel_file = request.FILES['excel_file']
            data = pd.read_excel(excel_file, engine='openpyxl')

            for index, row in data.iterrows():
                Tiendas.objects.create(
                    Cliente=row['Cliente'],
                    RIF=row['RIF'],
                    Direccion=row['Direccion'],
                )

            messages.success(request, 'Archivo de Excel importado con éxito.')
        except Exception as e:
            messages.error(request, f'Error al importar el archivo. No coinciden el formato con la aplicacion, revise el archivo e intente de nuevo')

        return redirect('Tiendas')

    return render(request, 'importarExcel.html')

from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .forms import ClientesFrm
from .models import Clientes

@login_required
@permission_required('clientes.add_clientes')
def addClient(request):
    if request.method == 'POST':
        form = ClientesFrm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente agregado con éxito')
                return redirect('Clientes') 
            except IntegrityError:
                if Clientes.objects.filter(Cedula=form.cleaned_data['Cedula']).exists():
                    messages.error(request, 'Ya existe un cliente con esa cédula.')
                elif Clientes.objects.filter(Correo=form.cleaned_data['Correo']).exists():
                    messages.error(request, 'Ya existe un cliente con ese correo electrónico.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ClientesFrm()

    context = {
        'Clients': form,
        'page_title': 'Oseed | Registrar Clientes'
    }
    return render(request, "AddCliente.html", context)


@login_required
@permission_required('clientes.change_clientes')
def updateClient(request, id):
    p = Clientes.objects.get(id=id)

    if request.method == 'POST':
        form = ClientesFrm(request.POST, instance=p)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Cliente actualizado con éxito')
                return redirect('Clientes')
            except IntegrityError:
                if Clientes.objects.filter(Cedula=form.cleaned_data['Cedula']).exclude(id=id).exists():
                    messages.error(request, 'Ya existe un cliente con esa cédula.')
                elif Clientes.objects.filter(Correo=form.cleaned_data['Correo']).exclude(id=id).exists():
                    messages.error(request, 'Ya existe un cliente con ese correo electrónico.')
    else:
        form = ClientesFrm(instance=p)

    context = {
        'Clients': form,
        'page_title': f'Oseed | {p.Nombre} {p.Apellido}'
    }
    return render(request, "UptCliente.html", context)

@login_required
@permission_required('clientes.delete_clientes')
def deleteClient(request, id):
    p = get_object_or_404(Clientes, id=id)
    p.delete()
    messages.success(request, "Cliente Eliminado con Exito")
    return redirect('Clientes')

class reporte_clientes(View):
    def get(self, request, *args, **kwargs):
        template_name = "reporteClientes.html"
        reporte = Clientes.objects.all().order_by('-id')
        data = {
            'entity': reporte
        }
        pdf = render_to_pdf(template_name, data)
        return HttpResponse(pdf, content_type='application/pdf')

@login_required
@permission_required('clientes.view_clientes')
def export_clientes_to_excel(request):
    tiendas = Clientes.objects.all().order_by('-id')

    data = [{      
        'Cliente': t.Nombre + " " + t.Apellido,
        'Cedula': t.Cedula,
        'Correo': t.Correo,
        'Telefono': t.Telefono,
        'Tienda': t.Tienda,
    } for t in tiendas]

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=tiendas.xlsx'

    df.to_excel(response, index=False)

    return response