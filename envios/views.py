# envios/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Encomienda
from .forms import EncomiendaForm
from config.choices import EstadoEnvio

@login_required
def dashboard(request): # Corregido: request en lugar de self
    encomiendas = Encomienda.objects.all()
    stats = {
        'total': encomiendas.count(),
        'activas': encomiendas.activas().count(),
        'en_transito': encomiendas.en_transito().count(),
        'con_retraso': encomiendas.con_retraso().count(),
    }
    recientes = encomiendas.order_by('-fecha_registro')[:5]
    return render(request, 'envios/dashboard.html', {'stats': stats, 'recientes': recientes})

@login_required
def encomienda_list(request):
    queryset = Encomienda.objects.con_relaciones()
    estado = request.GET.get('estado')
    if estado:
        queryset = queryset.filter(estado=estado)
    
    # Búsqueda
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(codigo__icontains=q)

    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'envios/encomienda_list.html', {
        'page_obj': page_obj, 
        'estados': EstadoEnvio.choices, 
        'estado_actual': estado
    })

@login_required
def encomienda_create(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        if form.is_valid():
            # Usamos nuestro método de clase para calcular costo automáticamente [cite: 5]
            encomienda = Encomienda.crear_con_costo_calculado(
                remitente=form.cleaned_data['remitente'],
                destinatario=form.cleaned_data['destinatario'],
                ruta=form.cleaned_data['ruta'],
                empleado=form.cleaned_data['empleado_registro'],
                descripcion=form.cleaned_data['descripcion'],
                peso_kg=form.cleaned_data['peso_kg'],
                volumen_cm3=form.cleaned_data['volumen_cm3'],
                observaciones=form.cleaned_data['observaciones']
            )
            messages.success(request, f'Encomienda {encomienda.codigo} registrada con éxito.') [cite: 6]
            return redirect('encomienda_list')
    else:
        form = EncomiendaForm()
    return render(request, 'envios/encomienda_form.html', {'form': form})

@login_required
def encomienda_detail(request, pk):
    encomienda = get_object_or_404(Encomienda.objects.con_relaciones(), pk=pk)
    return render(request, 'envios/encomienda_detail.html', {
        'encomienda': encomienda, 
        'historial': encomienda.historial.all()
    })