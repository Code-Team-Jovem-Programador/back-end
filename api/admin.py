from django.contrib import admin

from api import models

# Register your models here.
@admin.register(models.Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'quantidades', 'preco', 'categoria')
    list_display_links = ('nome', 'descricao', 'quantidades', 'preco', 'categoria')