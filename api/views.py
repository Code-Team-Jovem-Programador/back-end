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

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse

from .serializers import UserSerializer, PasswordChangeSerializer, PasswordResetSerializer

from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from django.contrib.auth.tokens import PasswordResetTokenGenerator

# Create your views here.

# Parte dedicada ao Usuário -----------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_activation_email(user, request)
        return Response(
            {"message": "Usuário registrado. Verifique seu e-mail para ativar a conta."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    activation_link = f'http://localhost:5173/activate?uidb64={uid}&token={token}'
    #activation_link = f'https://gerenciador-codeteam.onrender.com/activate?uidb64={uid}&token={token}'

    print(f"Link de ativação: {activation_link}")

    subject = "Confirme seu cadastro"
    message = f"Olá {user.username}, clique no link para ativar sua conta: {activation_link}"
    
    try:
        send_mail(subject, message, 'code.team.senac@gmail.com', [user.email])
        print(f"E-mail enviado para {user.email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Link inválido."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"message": "Conta ativada com sucesso!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    methods=['POST'],
    request_body= serializers.UserSerializer,
    tags=['Cadastro'],
)

@api_view(['POST'])
@permission_classes([AllowAny])

def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        send_activation_email(user, request)
        return Response(
            {"message": "Usuário registrado. Verifique seu e-mail para ativar a conta."},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Troca de senha ------------------------------------------------------------------------

@swagger_auto_schema(
    methods=['POST'],
    request_body= serializers.PasswordChangeSerializer,
    tags=['Mudar Senha'],
)

@api_view(['POST'])
@permission_classes ([IsAuthenticated])

def changePassword(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({"message": "Senha alterada com sucesso!"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Reset de senha --------------------------------------------------------------------

def send_password_reset_email(user, request):
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = request.build_absolute_uri(reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token}))

    subject = "Redefinição de Senha"
    message = f"Olá {user.username}, clique no link para redefinir sua senha: {reset_link}"
    send_mail(subject, message, 'code.team.senac@gmail.com', [user.email])

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetSerializer,
    tags=['password-reset'],
)

@api_view(['POST'])
@permission_classes([AllowAny])
def passwordReset(request):
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        send_password_reset_email(user, request)
        return Response({"message": "E-mail de redefinição de senha enviado."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetConfirmView(request, uidb64, token):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Link inválido."}, status=status.HTTP_400_BAD_REQUEST)

    if PasswordResetTokenGenerator().check_token(user, token):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        if new_password != confirm_password:
            return Response({"error": "As senhas não correspondem."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Senha redefinida com sucesso!"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Token inválido ou expirado."}, status=status.HTTP_400_BAD_REQUEST)

# Parte dedicada a Produtos ---------------------------------------------------------

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
@permission_classes([AllowAny])

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
@permission_classes([AllowAny])
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
        return Response({"message": "Produto deletado com sucesso."}, status=status.HTTP_204_NO_CONTENT)
    
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
    tags=['Lista de Produtos']
)    
@api_view(['GET'])
@permission_classes([AllowAny])
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

# Parte dedicada a extração de dados via banco de dados ------------------------------------------------------------------------------------------------
    
@api_view(['GET'])
@permission_classes([AllowAny])
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
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    )

    response['Content-Disposition'] = 'attachment; filename="Produtos.xlsx"'
    workbook.save(response)

    return response
    
@api_view(['GET'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
    