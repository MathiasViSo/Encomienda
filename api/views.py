# api/views.py
from rest_framework import status, generics, viewsets, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from envios.models import Encomienda, Empleado
from envios.serializers import EncomiendaSerializer, EncomiendaDetailSerializer

# --- 1. Function Based View (FBV) para Listar y Crear ---
@api_view(['GET', 'POST'])
def encomienda_list_fbv(request):
    if request.method == 'GET':
        encomiendas = Encomienda.objects.all()
        # many=True indica que vamos a serializar una lista de objetos, no solo uno
        serializer = EncomiendaSerializer(encomiendas, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = EncomiendaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- 2. Class Based View (CBV) para Detalle, Actualizar y Eliminar ---
class EncomiendaDetailAPI(APIView):
    def get_object(self, pk):
        return get_object_or_404(Encomienda, pk=pk)

    def get(self, request, pk):
        encomienda = self.get_object(pk)
        serializer = EncomiendaSerializer(encomienda)
        return Response(serializer.data)

    def put(self, request, pk):
        encomienda = self.get_object(pk)
        serializer = EncomiendaSerializer(encomienda, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        encomienda = self.get_object(pk)
        encomienda.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- 3. Vistas Genéricas (El verdadero poder de DRF) ---
class EncomiendaListCreateGenAPI(generics.ListCreateAPIView):
    """
    Endpoint súper-poderoso que hace lo mismo que la FBV, 
    pero además incluye paginación, filtros y búsquedas automáticas.
    """
    queryset = Encomienda.objects.all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated] # Protegemos el endpoint
    
    # Agregamos los motores de búsqueda y filtrado
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Configuramos por qué campos se puede filtrar y buscar
    filterset_fields = ['estado', 'ruta', 'remitente', 'destinatario']
    search_fields = ['codigo', 'descripcion', 'observaciones']
    ordering_fields = ['fecha_registro', 'costo_envio', 'peso_kg']


class EncomiendaDetailGenAPI(generics.RetrieveUpdateDestroyAPIView):
    """
    Maneja Ver Detalle (GET), Actualizar (PUT/PATCH) y Eliminar (DELETE).
    En 4 líneas de código reemplaza todo lo que hicimos en la CBV.
    """
    queryset = Encomienda.objects.all()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated]


# --- 4. ViewSets y Acciones Personalizadas (SESIÓN 6) ---
class EncomiendaViewSet(viewsets.ModelViewSet):
    """
    ViewSet maestro que maneja todo el CRUD de encomiendas automáticamente
    y permite agregar acciones extra.
    """
    queryset = Encomienda.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'ruta']
    search_fields = ['codigo']

    # Usamos un método para decidir qué serializer usar según la acción
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return EncomiendaDetailSerializer
        return EncomiendaSerializer

    @action(detail=False, methods=['get'])
    def con_retraso(self, request):
        """
        Endpoint: GET /api/v1/encomiendas/con_retraso/
        Muestra solo las encomiendas que ya pasaron su fecha estimada.
        """
        retrasadas = Encomienda.objects.con_retraso()
        # self.get_serializer aplica el serializador correspondiente
        serializer = self.get_serializer(retrasadas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """
        Endpoint: POST /api/v1/encomiendas/{id}/cambiar_estado/
        Permite actualizar el estado de forma segura e invalidar cachés.
        """
        encomienda = self.get_object()
        nuevo_estado = request.data.get('nuevo_estado')
        empleado_id = request.data.get('empleado_id')
        observacion = request.data.get('observacion', '')

        try:
            empleado = Empleado.objects.get(id=empleado_id)
            encomienda.cambiar_estado(nuevo_estado, empleado, observacion)
            
            # Devolvemos el objeto serializado con su nuevo estado
            return Response(EncomiendaSerializer(encomienda).data)
        except Empleado.DoesNotExist:
            return Response({'error': 'Empleado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)