import uuid
from django.db import models

# Create your models here.

class Produto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    descricao = models.TextField()
    quantidades = models.IntegerField()
    preco = models.FloatField()
    categoria = models.CharField(max_length=255)

    def __str__(self):
        return self.nome