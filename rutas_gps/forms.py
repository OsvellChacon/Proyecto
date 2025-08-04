from django import forms
from .models import Camiones

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Camiones
        fields = ['conductor', 'placa', 'marca', 'modelo', 'color', 'year', 'capacidad_tanque']
        widgets = {
            'conductor': forms.Select(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'capacidad_tanque': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_placa(self):
        placa = self.cleaned_data['placa']
        qs = Camiones.objects.filter(placa__iexact=placa)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)  # Excluir el actual si estamos editando

        if qs.exists():
            raise forms.ValidationError("Ya existe un vehículo con esa placa.")
        return placa
