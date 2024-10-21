from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

####################################################################################

class Producto(models.Model):
    descripcion = models.TextField(null=True)
    nombre = models.CharField(max_length=50)
    imagen = models.TextField(default='https://i1.sndcdn.com/artworks-000188509722-d50ce4-t240x240.jpg')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    cantidad = models.IntegerField(null=False, default=0)
    
    def __str__(self):
        return f"Producto {self.id} es de {self.nombre}"
    
