from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import models
from drf_yasg.utils import swagger_auto_schema
from . import serializers
from drf_yasg import openapi

# Create your views here.
@swagger_auto_schema(
    methods=['POST'],
    request_body=serializers.ProdutoSerializer,
    tags=['Produtos'],
)
@swagger_auto_schema(
    methods=['GET'],
    tags=['Produtos'],
)
                     
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])

def get_produtos(request):
    if request.method == 'GET':
        produtos = models.Produto.objects.all()
        serializer = serializers.ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':  
        serializer = serializers.ProdutoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(
    methods=['POST'],
    request_body= serializers.UserSerializer,
    tags=['Cadastro'],
)

@api_view(['POST'])
@permission_classes([AllowAny])

def register(request):
    serializer = serializers.UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"username": serializer.data['username']}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


id_param = openapi.Parameter(
    'id', openapi.IN_PATH, description="UUID do produto", type=openapi.TYPE_STRING, format='uuid'
)

@swagger_auto_schema(
    methods=['PUT'],
    request_body=serializers.ProdutoSerializer,
    tags=['Produtos by ID'],
    manual_parameters=[id_param],
)
@swagger_auto_schema(
    methods=['DELETE', 'GET'],
    tags=['Produtos by ID'],
    manual_parameters=[id_param],
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_produtos_id(request, id):
    try:
        produto = models.Produto.objects.get(id=id)
    except models.Produto.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = serializers.ProdutoSerializer(produto)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = serializers.ProdutoSerializer(produto, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        produto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)