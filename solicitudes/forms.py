from django import forms
from .models import Carrito, Factura
from inventario.models import Stock

class CarritoForm(forms.ModelForm):
    class Meta:
        model = Carrito
        fields = ['usuario', 'producto', 'cantidad']

    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad")
        producto = cleaned_data.get("producto")

        if producto and cantidad:
            if cantidad > producto.cantidad:
                raise forms.ValidationError(f'No hay suficiente stock para {producto.producto}. Solo hay {producto.cantidad} unidades disponibles.')

        return cleaned_data


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'tienda']

    def __init__(self, *args, **kwargs):
        super(FacturaForm, self).__init__(*args, **kwargs)

        # Ejemplo: self.fields['cliente'].widget.attrs.update({'class': 'form-control'})
