from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth import logout

def login_view(request):
    login_error = False  # Inicializamos el indicador de error
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
        login_error = True  # Establecemos el indicador de error si el inicio de sesión falla
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form, 'login_error': login_error})

def cerrar_sesion(request):
    logout(request)
    return redirect('login')