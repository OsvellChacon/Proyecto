from django import forms
from .models import *


class CategoriaFrm(forms.ModelForm):
    portada = forms.ImageField(
        label='Portada',
        required=False,
    )

    class Meta:
        model = Categorias
        fields = '__all__'


from django import forms
from django.forms import inlineformset_factory
from .models import Stock, PrecioPorUnidad, UnidadesVenta

class StockFrm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['producto', 'cantidad', 'unidad', 'existencia_min', 'precio', 'categoria', 'imagen']

    imagen = forms.ImageField(
        label='Imagen',
        validators=[validate_image_size, validate_image_dimensions],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidad'].widget.attrs.update({'class': 'form-control'})
        self.fields['categoria'].widget.attrs.update({'class': 'form-control'})

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        if Stock.objects.filter(producto=producto).exists():
            raise forms.ValidationError("Ya existe un producto con este nombre.")
        return producto

class StockActFrm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['producto', 'cantidad', 'unidad', 'existencia_min', 'precio', 'categoria', 'imagen']

    imagen = forms.ImageField(
        label='Imagen',
        required=False,  # <-- No requerido
        # validators=[validate_image_size],  # <-- Elimina validadores aquí, ya están en el modelo
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unidad'].widget.attrs.update({'class': 'form-control'})
        self.fields['categoria'].widget.attrs.update({'class': 'form-control'})

    def clean_producto(self):
        producto = self.cleaned_data.get('producto')
        # Excluir el producto actual de la validación
        qs = Stock.objects.filter(producto=producto)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un producto con este nombre.")
        return producto

class PrecioPorUnidadFrm(forms.ModelForm):
    class Meta:
        model = PrecioPorUnidad
        fields = ['producto', 'unidad_venta', 'precio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].widget.attrs.update({'class': 'form-control'})
        self.fields['unidad_venta'].widget.attrs.update({'class': 'form-control'})
        self.fields['precio'].widget.attrs.update({'class': 'form-control'})

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio


class TransaccionInventarioFrm(forms.ModelForm):
    class Meta:
        model = TransaccionInventario
        fields = ['producto', 'tipo', 'cantidad', 'usuario', 'motivo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo'].widget.attrs.update({'class': 'form-control'})
        self.fields['cantidad'].widget.attrs.update({'class': 'form-control'})
        self.fields['usuario'].widget.attrs.update({'class': 'form-control'})
        self.fields['motivo'].widget.attrs.update({'class': 'form-control'})

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad


class VariacionProductoFrm(forms.ModelForm):
    class Meta:
        model = VariacionProducto
        fields = ['producto', 'nombre_variacion', 'valor']

    def clean_nombre_variacion(self):
        nombre_variacion = self.cleaned_data.get('nombre_variacion')
        producto = self.cleaned_data.get('producto')
        if VariacionProducto.objects.filter(producto=producto, nombre_variacion=nombre_variacion).exists():
            raise forms.ValidationError("Ya existe una variación con este nombre para este producto.")
        return nombre_variacion

    def clean_valor(self):
        valor = self.cleaned_data.get('valor')
        if valor < 0:
            raise forms.ValidationError("El valor no puede ser negativo.")
        return valor

class BodegaForm(forms.ModelForm):
    class Meta:
        model = Bodega
        fields = ['codigo', 'nombre', 'ubicacion']

    codigo = forms.CharField(
        validators=[validate_codigo],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: BOD-0001'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['ubicacion'].widget.attrs.update({'class': 'form-control'})


class SubCategoriaForm(forms.ModelForm):
    class Meta:
        model = SubCategoria
        fields = ['nombre', 'categoria']

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        categoria = self.cleaned_data.get('categoria')
        if SubCategoria.objects.filter(nombre=nombre, categoria=categoria).exists():
            raise forms.ValidationError("Ya existe una subcategoría con este nombre en esta categoría.")
        return nombre


class UnidadesFrm(forms.ModelForm):
    class Meta:
        model = Unidades
        fields = ['unidad']

    def clean_unidad(self):
        unidad = self.cleaned_data.get('unidad')
        if Unidades.objects.filter(unidad=unidad).exists():
            raise forms.ValidationError("Ya existe una unidad con este nombre.")
        return unidad


class HistorialPrecioFrm(forms.ModelForm):
    class Meta:
        model = HistorialPrecio
        fields = ['producto', 'precio_anterior', 'precio_nuevo']

    def clean_precio_anterior(self):
        precio_anterior = self.cleaned_data.get('precio_anterior')
        if precio_anterior < 0:
            raise forms.ValidationError("El precio anterior no puede ser negativo.")
        return precio_anterior

    def clean_precio_nuevo(self):
        precio_nuevo = self.cleaned_data.get('precio_nuevo')
        if precio_nuevo < 0:
            raise forms.ValidationError("El precio nuevo no puede ser negativo.")
        return precio_nuevo


class StockBodegaFrm(forms.ModelForm):
    class Meta:
        model = StockBodega
        fields = ['producto', 'bodega', 'cantidad']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].widget.attrs.update({'class': 'form-control'})
        self.fields['bodega'].widget.attrs.update({'class': 'form-control'})
        self.fields['cantidad'].widget.attrs.update({'class': 'form-control'})

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad < 0:
            raise forms.ValidationError("La cantidad no puede ser negativa.")
        return cantidad
