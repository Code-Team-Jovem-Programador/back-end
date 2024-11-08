from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse
from openpyxl import Workbook
from . import serializers
from . import models
import csv

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
    
@api_view(['GET'])
def produtos_report_xlsx(request):
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