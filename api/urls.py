from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.get_produtos),
    path('export/', views.produtos_report_xlsx, name='produtos_report_xlsx'),
]