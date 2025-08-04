from django import forms
from .models import *

class TiendaFrm(forms.ModelForm):
    class Meta:
        model = Tiendas
        fields = '__all__'
        widgets = {
            'RIF': forms.TextInput(attrs={'placeholder': 'J-00000000-0'}),
        }
        
class ClientesFrm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'
        widgets = {
            'Cedula': forms.TextInput(attrs={'placeholder': '00.000.000'}),
            'Telefono': forms.TextInput(attrs={'placeholder':'Agrega un prefijo y despues el numero de telefono'}),
        }