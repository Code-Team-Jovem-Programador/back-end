import csv
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import models
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from openpyxl import Workbook
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
    
@api_view(['GET'])
def produtos_export_xlsx(request):
    produtos = models.Produto.objects.all()

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = 'Produtos'

    worksheet.append(['ID', 'PRODUTO', 'DESCRICAO', 'QUANTIDADE', 'PRECO', 'CATEGORIA'])

    for produto in produtos:
        worksheet.append([str(produto.id),
                          produto.nome,
                          produto.descricao,
                          produto.quantidades,
                          produto.preco,
                          produto.categoria])
        
    response = HttpResponse(
        content_type='application/vnd.opexmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename="Produtos.xlsx"'
    workbook.save(response)

    return response
    
@api_view(['GET'])
def produtos_export_csv(request):
    produtos = models.Produto.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Produtos.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'PRODUTO', 'DESCRICAO', 'QUANTIDADE', 'PRECO', 'CATEGORIA'])

    for produto in produtos:
        writer.writerow([str(produto.id),
                          produto.nome,
                          produto.descricao,
                          produto.quantidades,
                          produto.preco,
                          produto.categoria])
    
    return response

@api_view(['GET'])
def produtos_export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Produtos.pdf"'

    pdf_canvas = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = landscape(A4)

    pdf_canvas.setFont("Helvetica-Bold", 12)
    pdf_canvas.drawString(100, height - 50, "Relatório de Produtos")

    pdf_canvas.setFont("Helvetica-Bold", 8)
    pdf_canvas.drawString(30, height - 60, "ID")
    pdf_canvas.drawString(200, height - 60, "PRODUTO")
    pdf_canvas.drawString(350, height - 60, "DESCRICAO")
    pdf_canvas.drawString(570, height - 60, "QUANTIDADE")
    pdf_canvas.drawString(630, height - 60, "PRECO")
    pdf_canvas.drawString(700, height - 60, "CATEGORIA")

    y_position = height - 80  
    produtos = models.Produto.objects.all()
    
    for produto in produtos:
        if y_position < 40:
            pdf_canvas.showPage()
            y_position = height - 40 

        pdf_canvas.setFont("Helvetica", 8)
        pdf_canvas.drawString(30, y_position, str(produto.id))
        pdf_canvas.drawString(200, y_position, produto.nome[:15])
        pdf_canvas.drawString(350, y_position, produto.descricao[:25])
        pdf_canvas.drawString(570, y_position, str(produto.quantidades))
        pdf_canvas.drawString(630, y_position, f"R${produto.preco:.2f}")
        pdf_canvas.drawString(700, y_position, produto.categoria[:15])

        y_position -= 20
    
    pdf_canvas.save()
    return response
    