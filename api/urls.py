from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.get_produtos),
    path('export/xlsx/', views.produtos_report_xlsx, name='produtos_report_xlsx'),
    path('export/csv/', views.produtos_report_csv, name='produtos_report_csv'),
    path('export/pdf/', views.produtos_report_pdf, name='produtos_resport_pdf'),
    path('produtos/', views.get_produtos),
    path('register/', views.register),
    path('produtos/<uuid:id>', views.get_produtos_id),
    path('produtos/listar', views.listar_produtos),
]
