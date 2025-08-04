from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Cargos
from django.contrib.auth.forms import UserChangeForm

class CustomUserCreationForm(UserCreationForm):
    cedula = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': '00.000.000'}))
    telefono = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'placeholder': 'Agrega un prefijo y después el número de teléfono'}))
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'password1', 
            'password2', 
            'nombre', 
            'apellido', 
            'cedula', 
            'direccion', 
            'email', 
            'telefono', 
            'cargo', 
            'imagen_perfil'
        )

class CustomUserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'nombre', 
            'apellido', 
            'cedula', 
            'direccion', 
            'email', 
            'telefono', 
            'cargo', 
            'imagen_perfil'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eliminamos los campos de contraseña
        self.fields.pop('password')

    def save(self, commit=True):
        user = super().save(commit=False)
        # No hacemos nada con la contraseña aquí
        if commit:
            user.save()
        return user

class CargosForm(forms.ModelForm):
    class Meta:
        model = Cargos
        fields = '__all__'
