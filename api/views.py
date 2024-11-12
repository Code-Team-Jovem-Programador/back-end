from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import models
from drf_yasg.utils import swagger_auto_schema
from . import serializers
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination

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
    
class ProdutoPagination(PageNumberPagination):
    page_size = 10  
    page_size_query_param = 'page_size' 
    max_page_size = 100  

@swagger_auto_schema(
    methods=['GET'],
    operation_description="Lista todos os produtos com a possibilidade de filtrar por categoria e paginar os resultados.",
    manual_parameters=[
        openapi.Parameter('categoria', openapi.IN_QUERY, description="Filtrar produtos por categoria", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Número da página", type=openapi.TYPE_INTEGER, default=1),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Número de itens por página", type=openapi.TYPE_INTEGER, default=10)
    ],
    tags=['Produtos']
)    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def listar_produtos(request):
    categoria = request.query_params.get('categoria', None)
    if categoria:
        produtos = models.Produto.objects.filter(categoria__icontains=categoria)
    else:
        produtos = models.Produto.objects.all()
    paginator = ProdutoPagination()
    paginated_produtos = paginator.paginate_queryset(produtos, request)
    serializer = serializers.ProdutoSerializer(paginated_produtos, many=True)
    return paginator.get_paginated_response(serializer.data)