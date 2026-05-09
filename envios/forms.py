# envios/forms.py
from django import forms
from .models import Encomienda, Cliente, Ruta, Empleado
from config.choices import EstadoGeneral

class EncomiendaForm(forms.ModelForm):
    class Meta:
        model = Encomienda
        # Campos que el usuario llenará manualmente
        fields = [
            'descripcion', 'peso_kg', 'volumen_cm3', 
            'remitente', 'destinatario', 'ruta', 
            'empleado_registro', 'observaciones'
        ]
        # Diseño con Bootstrap
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'peso_kg': forms.NumberInput(attrs={'class': 'form-control'}),
            'volumen_cm3': forms.NumberInput(attrs={'class': 'form-control'}),
            'remitente': forms.Select(attrs={'class': 'form-select'}),
            'destinatario': forms.Select(attrs={'class': 'form-select'}),
            'ruta': forms.Select(attrs={'class': 'form-select'}),
            'empleado_registro': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtro: Solo mostrar clientes y rutas con estado ACTIVO (1) 
        self.fields['remitente'].queryset = Cliente.objects.filter(estado=EstadoGeneral.ACTIVO)
        self.fields['destinatario'].queryset = Cliente.objects.filter(estado=EstadoGeneral.ACTIVO)
        self.fields['ruta'].queryset = Ruta.objects.filter(estado=EstadoGeneral.ACTIVO)