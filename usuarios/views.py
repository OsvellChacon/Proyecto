from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CargosForm,CustomUserUpdateForm
from .models import CustomUser, Cargos
from .utils import render_to_pdf 
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
from django.views.generic import View
from django.db.models import Q
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from auditlog.models import LogEntry
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from openpyxl.utils import get_column_letter
from openpyxl import Workbook

@login_required
@permission_required('usuarios.view_customuser')
def usuarios(request):

    total_usuarios = CustomUser.objects.count()
    Maki = CustomUser.objects.all().order_by('-id')
    
    # Agregar paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(Maki, 5)

    try:
        Maki = paginator.page(page)
    except PageNotAnInteger:
        Maki = paginator.page(1)
    except EmptyPage:
        Maki = paginator.page(paginator.num_pages)
    
    context = {
        'total_usuarios': total_usuarios,
        'Zenin': Maki,
        'page_title': 'Oseed | Gestion de Usuarios',
        'paginator': paginator
    }

    return render(request, "usuarios.html", context)

@login_required
@permission_required('usuarios.view_customuser')
def user_list(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.filter(is_superuser=False).order_by('-id')

    if query:
        users = users.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(cedula__icontains=query)
        )

        if not users.exists():
            messages.warning(request, 'No se encontraron usuarios con los criterios de búsqueda proporcionados.')

    # Agregar paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(users, 5)  # Muestra 5 usuarios por página

    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
        
    megumi = {
        'users': users,
        'page_title': 'Oseed | Usuarios'
    }

    return render(request, 'vista_usuarios.html', megumi)

@login_required
@permission_required('usuarios.delete_customuser')
def view_user_permissions(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    permissions = user.user_permissions.all()  # Obtener los permisos del usuario
    return render(request, 'user_permissions_view.html', {'user': user, 'permissions': permissions})

@login_required
@permission_required('usuarios.view_customuser', raise_exception=True)
def detalles_usuario(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    
    user_action_logs = LogEntry.objects.filter(actor_id=user_id)[:3]
    
    paginator = Paginator(user_action_logs, 4)
    page = request.GET.get('page')
    try:
        user_action_logs = paginator.page(page)
    except PageNotAnInteger:
        user_action_logs = paginator.page(1)
    except EmptyPage:
        user_action_logs = paginator.page(paginator.num_pages)
    
    all_permissions = Permission.objects.all()

    # Calcula la cantidad de permisos del usuario
    user_permissions_count = user.user_permissions.count()

    # Asigna un valor válido a permission_id
    permission_id = 1  # O según tu lógica de negocio
    
    Itadori = {
        'user': user, 
        'user_action_logs': user_action_logs, 
        'all_permissions': all_permissions, 
        'user_permissions_count': user_permissions_count, 
        'permission_id': permission_id,
        'page_title': f'Oseed | {user.nombre} {user.apellido}'
    }
    
    return render(request, 'user_details.html', Itadori)

@login_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado con éxito.')
            return redirect('vista_usuarios')
        else:
            messages.error(request, 'Error al crear el usuario. Por favor, corrige los errores.')
    else:
        form = CustomUserCreationForm()

    Nanami = {
        'form': form,
        'page_title': 'Oseed | Crear Usuarios'
    }

    return render(request, 'crear_usuario.html', Nanami)

@login_required
@permission_required('usuarios.change_customuser')
def update_user(request, user_id):
    user = CustomUser.objects.get(pk=user_id)

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado con éxito.')
            return redirect('vista_usuarios')
    else:
        form = CustomUserUpdateForm(instance=user)
        
    Nobara = {
        'form': form, 
        'user': user,
        'page_title': f'Oseed | {user.nombre} {user.apellido}'
    }

    return render(request, 'act_usuario.html', Nobara)

@login_required
@permission_required('usuarios.delete_customuser')
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, 'Usuario eliminado con éxito.')
    return redirect('vista_usuarios')

@login_required
@permission_required('usuarios.delete_customuser')
def asignar_permiso(request, user_id, permission_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    permission = get_object_or_404(Permission, pk=permission_id)

    if request.method == 'POST':
        permisos_seleccionados = request.POST.getlist('permisos')
        user.user_permissions.set(permisos_seleccionados)
        messages.success(request, "Permisos actualizados correctamente.")
        return redirect('detalles_usuario', user_id=user_id)
    
    messages.error(request, "Método de solicitud no permitido.")
    return redirect('detalles_usuario', user_id=user_id)

@login_required
@permission_required('usuarios.delete_customuser')
def quitar_permiso(request, user_id, permission_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    permission = get_object_or_404(Permission, pk=permission_id)
    
    try:
        user.user_permissions.remove(permission)
        messages.success(request, "Permiso quitado correctamente.")
    except Permission.DoesNotExist:
        messages.error(request, "El permiso seleccionado no existe.")
    except CustomUser.DoesNotExist:
        messages.error(request, "El usuario seleccionado no existe.")

    return redirect('detalles_usuario', user_id=user_id)

@login_required
@permission_required('usuarios.view_cargos')
def ver_cargos(request):
    query = request.GET.get('q', '')
    itadori = Cargos.objects.all().order_by('-id')

    # Filtro
    if query:
        itadori = itadori.filter(
            Q(Nombre__icontains=query)
        )

        if not itadori.exists():
            messages.warning(request, 'No se encontraron resultados con los criterios de búsqueda proporcionados.')

    # Paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(itadori, 5)

    try:
        cargos = paginator.page(page)
    except PageNotAnInteger:
        cargos = paginator.page(1)
    except EmptyPage:
        cargos = paginator.page(paginator.num_pages)
        
    JoGoat = {
        'sukuna': itadori, 
        'paginator': paginator,
        'page_title': 'Oseed | Gestión de Cargos'
    }

    return render(request, "ver_cargos.html", JoGoat)

@login_required
@permission_required('usuarios.add_cargos')
def create_cargo(request):
    if request.method == 'POST':
        form = CargosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo creado con éxito.')
            return redirect('view_cargo')
    else:
        form = CargosForm()
        
    Mahito = {
        'form': form,
        'page_title': 'Oseed | Crear Cargos'
    }

    return render(request, 'crear_cargo.html', Mahito)

@login_required
@permission_required('usuarios.change_cargos')
def update_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargos, pk=cargo_id)

    if request.method == 'POST':
        form = CargosForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo actualizado con éxito.')
            return redirect('view_cargo')
    else:
        form = CargosForm(instance=cargo)
        
    Aoi = {
        'form': form, 
        'cargo': cargo,
        'page_title': f'Oseed | {cargo.Nombre}'
    }

    return render(request, 'act_cargo.html', Aoi)

@login_required
@permission_required('usuarios.delete_cargos')
def delete_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargos, id=cargo_id)
    cargo.delete()
    messages.success(request, 'Cargo eliminado con éxito.')
    return redirect('view_cargo')

class reporte_usuarios_pdf(View):
    def get(self, request, *args, **kwargs):
        template_name = "reporteUsuarios.html"
        usuarios = CustomUser.objects.all().order_by('-id')
        data = {'usuarios': usuarios}
        print(usuarios)  # Imprime los usuarios en la consola para verificar
        pdf = render_to_pdf(template_name, data)
        return HttpResponse(pdf, content_type='application/pdf')

@login_required
@permission_required('usuarios.view_customuser')
def exportar_usuarios_a_excel(request):
    usuarios = CustomUser.objects.all().order_by('-id')

    data = [{
        'Nombre': u.nombre,
        'Apellido': u.apellido,
        'Cedula': u.cedula,
        'Telefono': u.telefono,
        'Direccion': u.direccion,
        'Cargo': u.cargo.Nombre if u.cargo else '',
    } for u in usuarios]

    df = pd.DataFrame(data)

    # Convertir el DataFrame a un archivo Excel utilizando el motor 'openpyxl'
    with pd.ExcelWriter('usuarios.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']

        # Ajustar automáticamente el tamaño de las columnas
        for column_cells in worksheet.columns:
            max_length = 0
            column = column_cells[0].column  # Columna con 1 base
            column_letter = get_column_letter(column)  # Letra de columna

            # Encontrar la celda más larga en cada columna
            for cell in column_cells:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass

            # Ajustar el ancho de la columna basándose en el valor más largo
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column_letter].width = adjusted_width

    # Enviar la respuesta con el archivo ajustado
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=usuarios.xlsx'
    workbook.save(response)

    return response