from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
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
    
@api_view(['GET'])
def produtos_report_csv(request):
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
def produtos_report_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Produtos.pdf"'

    pdf_canvas = canvas.Canvas(response, pagesize=landscape(A4))
    width, height = A4

    pdf_canvas.setFont("Helvetica-Bold", 14)
    pdf_canvas.drawString(100, height - 50, "Relatório de Produtos")

    pdf_canvas.setFont("Helvetica-Bold", 8)
    pdf_canvas.drawString(30, height - 70, "ID")
    pdf_canvas.drawString(100, height - 80, "PRODUTO")
    pdf_canvas.drawString(200, height - 100, "DESCRICAO")
    pdf_canvas.drawString(300, height - 80, "QUANTIDADE")
    pdf_canvas.drawString(350, height - 50, "PRECO")
    pdf_canvas.drawString(400, height - 100, "CATEGORIA")

    y_position = height - 100  
    produtos = models.Produto.objects.all()
    
    for produto in produtos:
        pdf_canvas.setFont("Helvetica", 10)
        pdf_canvas.drawString(30, y_position, str(produto.id))
        pdf_canvas.drawString(100, y_position, produto.nome)
        pdf_canvas.drawString(200, y_position, produto.descricao)
        pdf_canvas.drawString(300, y_position, f"{produto.quantidades}")
        pdf_canvas.drawString(350, y_position, f"R${produto.preco:.2f}")
        pdf_canvas.drawString(400, y_position, produto.categoria)
        
        y_position -= 20
        
        if y_position < 40:
            pdf_canvas.showPage()
            y_position = height - 40

    pdf_canvas.save()

    return response