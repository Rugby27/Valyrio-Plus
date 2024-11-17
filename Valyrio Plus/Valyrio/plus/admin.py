from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Trabajador)
admin.site.register(Repartidor)
admin.site.register(InversionColeccion)
admin.site.register(MetodoPago)
admin.site.register(DetalleInversion)
admin.site.register(Regalias)
admin.site.register(Compra)
admin.site.register(DetalleCompra)
admin.site.register(Envio)
admin.site.register(Devolucion)
