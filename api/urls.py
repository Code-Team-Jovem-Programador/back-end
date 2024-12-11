from django.urls import path
from . import views
from .views import register, activate_account, changePassword, passwordReset,passwordResetConfirmView

urlpatterns = [
    path('produtos/', views.get_produtos),
    path('register/', register, name='register'),
    path('produtos/<uuid:id>', views.get_produtos_id),
    path('produtos/listar', views.listar_produtos),
    path('export/xlsx/', views.produtos_export_xlsx, name='produtos_export_xlsx'),
    path('export/csv/', views.produtos_export_csv, name='produtos_export_csv'),
    path('export/pdf/', views.produtos_export_pdf, name='produtos_export_pdf'),
    path('activate/<str:uidb64>/<str:token>/', activate_account, name='activate'),
    path('change-password/', changePassword, name='change_password'),
    path('password-reset/', passwordReset, name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', passwordResetConfirmView, name='password-reset-confirm'),
]
