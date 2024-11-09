from django.urls import path
from . import views

urlpatterns = [
    path('produtos/', views.get_produtos),
    path('register/', views.register),
    path('produtos/<uuid:id>', views.get_produtos_id),
]
