from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone
class User(AbstractUser):
    pass

####################################################################################

class Producto(models.Model):
    descripcion = models.CharField(max_length=100, default='Sin descripción')
    precio = models.FloatField()
    nombre = models.CharField(max_length=40)
    cantidad = models.IntegerField()
    peso = models.FloatField()
    imagen = models.ImageField(upload_to="productos", null=True)

    def __str__(self):
        return f"Producto {self.id} es {self.nombre} con precio {self.precio}"


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=8)
    cedula = models.CharField(max_length=25)
    correo = models.EmailField(max_length=25, null=True, blank=True)
    contraseña = models.CharField(max_length=30)

    def __str__(self):
        return f"Cliente {self.nombre} es {self.nombre} {self.apellido}"

class Trabajador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=8)
    cedula = models.CharField(max_length=25)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return f"Trabajador {self.id} es {self.nombre} {self.apellido}"


class Repartidor(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    telefono = models.CharField(max_length=8)
    cedula = models.CharField(max_length=25)
    matricula = models.CharField(max_length=25)

    def __str__(self):
        return f"Repartidor {self.id} es {self.nombre} {self.apellido}"


class InversionColeccion(models.Model):
    total_inversion = models.FloatField()
    fecha_inversion = models.DateField(auto_now_add=True)
    confirmada = models.BooleanField(default=0)

    def __str__(self):
        return f"Inversión {self.id} con total de {self.total_inversion}"


class MetodoPago(models.Model):
    tipo_metodo_pago =  models.CharField(max_length=20)

    def __str__(self):
        return self.tipo_metodo_pago


class DetalleInversion(models.Model):
    inversion_coleccion = models.ForeignKey(InversionColeccion, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f"Detalle de Inversión {self.id} - Producto {self.producto.nombre} con cantidad {self.cantidad}"


class Regalias(models.Model):
    cantidad = models.IntegerField()
    monto_total = models.FloatField()
    fecha_regalia = models.DateField(auto_now_add=True)
    beneficiado = models.CharField(max_length=50)
    justificacion = models.CharField(max_length=50)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    def __str__(self):
        return f"Regalía {self.id} para {self.beneficiado}"


class Compra(models.Model):
    comprobante = models.ImageField(upload_to="comprobantes", null=True)
    total = models.FloatField()
    fecha_compra = models.DateField()
    tipo_compra = models.BooleanField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    comfimada = models.BooleanField(default=0) #Si ya se pago
    Cancelada = models.BooleanField(default=0) # si el cliente rechaso el envio   
    
    def __str__(self):
        return f"Compra {self.id} de {self.total} por "


class DetalleCompra(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        if self.producto:
            return f"Detalle de Compra {self.id} - {self.cantidad} unidades de {self.producto.nombre}"
        return f"Detalle de Compra {self.id} - Producto no especificado"


class Envio(models.Model):
    direccion = models.CharField(max_length=150, blank=True) 
    peso = models.FloatField(null=True, blank=True) 
    telefono = models.CharField(max_length=8, blank=True)
    tarifa_envio = models.FloatField(null=True, blank=True)
    repartidor = models.ForeignKey(Repartidor, on_delete=models.CASCADE, blank=True, null=True)
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)

    def __str__(self):
        return f"Envío {self.id} a {self.direccion}"


class Devolucion(models.Model):
    descripcion = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to="devoluciones", null=True)
    fecha_devolucion = models.DateField(auto_now_add=True)
    detalle_compra = models.ForeignKey(DetalleCompra, on_delete=models.CASCADE,null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    aceptada = models.BooleanField(default=0)

    def __str__(self):
        return f"Devolución {self.id} por {self.cliente.nombre}"