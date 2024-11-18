from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q, Count
from .models import *

#para verificar su un user es staff(los trabajadores son staff)

def is_staff_user(user):
    return user.is_staff
# Decorador que aplica la restricción
staff_required = user_passes_test(is_staff_user, login_url='loggin')  

""" 
Cliente(49):
    login cliente
    register cliente
    perfil
    agregar al carrito
    index
Admin(191):
    login Trabajador
    Register Trabajador
    trabajadores
    productos(stock)
    envios
    asignar repartidor
    Venta en el local
    Compras
    Devolucion
    Aceptar Devolucion
    Regalias
    Registrar regalias
    Inversiones
    Registrar inversiones
Ambos(451):
    logout
    realizar compra
    carrito
    Producto especifico
    calcular total


 """

#----------------------------------------------------------Clientes-----------------------------------------------------------#
######################################################
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "plus/cliente/index.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "plus/cliente/login.html")
    

######################################################
def register(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        telefono = request.POST["telefono"]
        cedula = request.POST["cedula"]
        correo = request.POST["correo"]
        contraseña = request.POST["contraseña"]
        confirmacion = request.POST["confirmacion"]

        # Verificar que las contraseñas coincidan
        if contraseña != confirmacion:
            return render(request, "plus/cliente/register.html", {
                "message": "Las contraseñas deben coincidir."
            })

        # Intentar crear el nuevo usuario y el cliente
        try:
            # Crear el User
            user = User.objects.create_user(
                username=correo,  # Usamos el correo como el nombre de usuario
                email=correo,
                password=contraseña  # Almacenamos la contraseña de manera segura
            )
            user.save()

            # Crear el Cliente asociado al User
            cliente = Cliente.objects.create(
                user=user,  # Asociamos el usuario creado al cliente
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                cedula=cedula,
                correo=correo,
                contraseña=contraseña  # Esto se puede dejar si deseas mostrar la contraseña, aunque generalmente no se almacena
            )
            cliente.save()
        except IntegrityError:
            return render(request, "plus/cliente/register.html", {
                "message": "El cliente ya existe."
            })

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "plus/cliente/register.html")

######################################################
def perfil(request):
    user = Cliente.objects.get(user=request.user)
    compras = Compra.objects.filter(cliente=user)
    envios = Envio.objects.filter(compra__in=compras)
    compras_envios = zip(compras, envios)
    can = Compra.objects.filter(cliente=user).count()

    return render(request, "plus/cliente/perfil.html", {
        "User": user,
        "Compras_Envios": compras_envios,
        "can" :can  # Pasa el objeto combinado
    })

######################################################
@login_required
def agregarCarrito(request):
    if request.method == "POST":
        producto_id = request.POST.get("prod")
        
        if producto_id is None or not producto_id.isdigit():
            return HttpResponse("ID del producto inválido")
        
        # Obtener el cliente asociado al usuario actual
        cliente = request.user.cliente  # Esto obtiene el cliente asociado al usuario logueado
        if not cliente:
            return HttpResponse("El usuario no tiene un cliente asociado.")
        
        produc = get_object_or_404(Producto, id=producto_id)

        compra = Compra.objects.filter(cliente=cliente, comfimada=False).first()

        if compra:
            # Si existe una compra no confirmada, agregamos el producto al detalle de compra
            DetalleCompra.objects.create(
                producto=produc,
                compra=compra,
                cantidad=1
            )
        else:
            
            metodo_pago = get_object_or_404(MetodoPago, tipo_metodo_pago="Efectivo")
            
            # Crear una nueva compra
            newC = Compra.objects.create(
                comprobante="Hola",
                total=0,
                fecha_compra="2024-11-11",
                tipo_compra=False,
                cliente=cliente,
                metodo_pago=metodo_pago,
                comfimada=False
            )
            DetalleCompra.objects.create(
                producto=produc,
                compra=newC,
                cantidad=1
            )

        return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("index"))  

#---------------------------------Productos------------------------------#
######################################################
def index(request):
    todoslosproductos = Producto.objects.filter(cantidad__gt = 0).order_by("-id")
    return render(request, "plus/cliente/index.html", {
        "todoslosproductos": todoslosproductos
    })



#----------------------------------------------------------Admins--------------------------------------------------------------#
######################################################
def login_traba(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]

        print(username)
        print(password)
        user = authenticate(request, username=username, password=password)
        #user = User.objects.get(username="Conde18")
        print(user)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("prods"))
        else:
            return render(request, "plus/administracion/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        logout(request)
        return render(request, "plus/administracion/login.html")

######################################################
@staff_required
def register_traba(request):
    if request.method == "POST":
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        telefono = request.POST["telefono"]
        cedula = request.POST["cedula"]
        correo = request.POST["correo"]
        contraseña = request.POST["contraseña"]
        fecha_nacimiento = request.POST["fecha"]  # Corregir 'POSR' a 'POST'

        # Intentar crear el nuevo usuario y el trabajador
        try:
            # Crear el User
            user = User.objects.create_user(
                username=nombre,  # Usamos el nombre como el nombre de usuario
                email=correo,
                password=contraseña  # Almacenamos la contraseña de manera segura
            )
            user.save()

            # Crear el Trabajador asociado al User
            trabajador = Trabajador.objects.create(
                user=user,  # Asociamos el usuario creado al trabajador
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                cedula=cedula,
                fecha_nacimiento=fecha_nacimiento
            )
            trabajador.save()
        except IntegrityError:
            return render(request, "plus/administracion/register.html", {
                "message": "El trabajador ya existe."
            })

        return HttpResponseRedirect(reverse("prods"))
    else:
        return render(request, "plus/administracion/register.html")

    
@staff_required
def trabajadores(request):
    trabajadores_con_compras = Trabajador.objects.annotate(num_compras=Count('compra'))
    repartidores_con_envios = Repartidor.objects.annotate(num_envios=Count('envio'))
    context = {
    'trabajadores': trabajadores_con_compras,
    'repartidores': repartidores_con_envios,
    }
    return render(request,"plus/administracion/Trabajadores.html", context)

@staff_required
def prods(request):
    productos = Producto.objects.all().order_by("-id")
    return render(request, "plus/administracion/stock.html", {
        "productos": productos
    })

@staff_required
def envios(request):
    # Obtener los envíos con y sin repartidor
    envios_con_repartidor = Envio.objects.filter(repartidor__isnull=False)
    envios_sin_repartidor = Envio.objects.filter(repartidor__isnull=True)

    # Obtener todos los repartidores disponibles
    repartidores = Repartidor.objects.all()

    context = {
        'envios_con_repartidor': envios_con_repartidor,
        'envios_sin_repartidor': envios_sin_repartidor,
        'repartidores': repartidores,
    }
    return render(request, 'plus/administracion/envios.html', context)
@staff_required
def asignar_repartidor(request, envio_id):
    if request.method == 'POST':
        envio = get_object_or_404(Envio, pk=envio_id)
        repartidor_id = request.POST.get('repartidor')
        repartidor = Repartidor.objects.get(pk=repartidor_id)
        envio.repartidor = repartidor
        envio.save()

    return redirect('envios')  # Redirige de nuevo a la vista de envíos

@staff_required
def compraLocal(request):
    if request.method == "POST":
        producto_id = request.POST.get("prod")
        
        if producto_id is None or not producto_id.isdigit():
            return HttpResponse("ID del producto inválido")
        
        user = User.objects.get(username="Conde18")

# Verifica si tiene un trabajador asociado
        print(hasattr(user, 'trabajador'))  # Esto debería devolver True
        if hasattr(user, 'trabajador'):
            print(user.trabajador)

        cliente = request.user.trabajador
        print(cliente)
        if not cliente:
            return HttpResponse("El usuario no tiene un cliente asociado.")
        
        produc = get_object_or_404(Producto, id=producto_id)

        compra = Compra.objects.filter(trabajador=cliente, comfimada=False).first()

        if compra:
            DetalleCompra.objects.create(
                producto=produc,
                compra=compra,
                cantidad=1
            )
        else:
            
            metodo_pago = get_object_or_404(MetodoPago, tipo_metodo_pago="Efectivo")
            
            # Crear una nueva compra
            newC = Compra.objects.create(
                comprobante="Hola",
                total=0,
                fecha_compra="2024-11-11",
                tipo_compra=True,
                trabajador=cliente,
                metodo_pago=metodo_pago,
                comfimada=False
            )
            DetalleCompra.objects.create(
                producto=produc,
                compra=newC,
                cantidad=1
            )

        return HttpResponseRedirect(reverse("prods"))

    return HttpResponseRedirect(reverse("prods"))  

@staff_required 
def compras(request):
    registro = Compra.objects.all()
    return render(request, "plus/administracion/compras.html", {
        "compras": registro
        })

@staff_required
def devolucion(request):
    devoluciones_confirmadas = Devolucion.objects.filter(aceptada=True)
    devoluciones_no_confirmadas = Devolucion.objects.filter(aceptada=False)
    return render(request, "plus/administracion/devoluciones.html", {
        "devoluciones_confirmadas": devoluciones_confirmadas,
        "devoluciones_no_confirmadas": devoluciones_no_confirmadas
    })

@staff_required
def aceptarDevolucion(request, devolucion_id):
    if request.method == 'POST':
        dev = get_object_or_404(Devolucion, pk=devolucion_id)
        dev.aceptada = True
        dev.save() 
        return redirect('devolucion')


@staff_required  
def regalias(request):
    regalia = Regalias.objects.all()
    return render(request, "plus/administracion/regalia.html",{
        'regalias' : regalia
    })

@staff_required
def registro_regalias(request):
    if request.method == 'POST':
        cantidad = request.POST['cantidad']
        monto_total = request.POST['monto_total']
        fecha_regalia = request.POST['fecha_regalia']
        beneficiado = request.POST['beneficiado']
        justificacion = request.POST['justificacion']
        producto_id = request.POST['producto']
        producto = Producto.objects.get(pk=producto_id)

        # Crear la nueva instancia de Regalias
        Regalias.objects.create(
            cantidad=cantidad,
            monto_total=monto_total,
            fecha_regalia=fecha_regalia,
            beneficiado=beneficiado,
            justificacion=justificacion,
            producto=producto
        )
        return redirect('registro_regalias')  # Cambia 'success_page' al nombre de tu vista de éxito

    productos = Producto.objects.all()
    return render(request, 'plus/administracion/Newregalias.html', {'productos': productos})

@staff_required
def inversion(request):
    inversiones = InversionColeccion.objects.all()
    for inversion in inversiones:
        # Obtener los detalles asociados a esta inversión
        inversion.detalles = DetalleInversion.objects.filter(inversion_coleccion=inversion)
    return render(request, "plus/administracion/invesion.html",{
        'inversiones' : inversiones,
    })

@staff_required
def registro_inversion(request):
    productos = Producto.objects.all()

    if request.method == 'POST':
        # Primero se obtiene y guarda la inversión
        total_inversion = request.POST['total_inversion']
        fecha_inversion = request.POST['fecha_inversion']
        
        # Crear la inversión
        inversion = InversionColeccion.objects.create(
            total_inversion=total_inversion,
            fecha_inversion=fecha_inversion
        )

        # Luego se obtiene y guarda los detalles de inversión
        productos_seleccionados = request.POST.getlist('producto')  # Lista de IDs de productos
        cantidades = request.POST.getlist('cantidad')  # Lista de cantidades correspondientes a los productos

        for producto_id, cantidad in zip(productos_seleccionados, cantidades):
            producto = Producto.objects.get(id=producto_id)
            
            # Actualizar la cantidad del producto
            producto.cantidad += int(cantidad)  # Sumar la cantidad invertida
            producto.save()  # Guardar el producto con la nueva cantidad

            # Crear el detalle de inversión
            DetalleInversion.objects.create(
                inversion_coleccion=inversion,
                producto=producto,
                cantidad=cantidad
            )

        return redirect('inversion') 

    return render(request, 'plus/administracion/Newinversion.html', {'productos': productos})

#----------------------------------------------------------Ambos--------------------------------------------------------------#
######################################################
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


######################################################
def realizar_compra(request):
    if request.method == "POST":
        detalles = DetalleCompra.objects.filter(compra__cliente=request.user.cliente, compra__comfimada=False)
        direccion = request.POST.get("direccion")
        departamento = request.POST.get("departamento")
        telefono = request.POST.get("telefono")
        tienda = request.POST.get("cliente")
        Nombre = request.POST.get("name")  # Corregido: se usaba POT en lugar de POST

        for detalle in detalles:
            # Obtener el valor enviado en el input de cantidad de cada producto
            cantidad = request.POST.get(f"cantidad_{detalle.id}")
            if cantidad and cantidad.isdigit():
                detalle.cantidad = int(cantidad)  # Actualizar la cantidad en la base de datos
                detalle.save()
                producto = detalle.producto
                producto.cantidad = producto.cantidad - int(cantidad)
                producto.save()

        compra = Compra.objects.filter(cliente=request.user.cliente, comfimada=False).first()

        if request.user.is_staff:
            # Buscar el cliente con el correo proporcionado
            try:
                cliente = Cliente.objects.get(correo=tienda)
            except Cliente.DoesNotExist:
                # Si el cliente no existe, crear uno nuevo con valores predeterminados
                cliente = Cliente.objects.create(
                    nombre=Nombre,
                    apellido=" ",  # Valor por defecto
                    telefono="00000000",  # Valor por defecto
                    cedula="000000000",  # Valor por defecto
                    correo=tienda,
                    contraseña="defaultpassword"  # Valor por defecto
                )

            if compra:
                compra.total = calcular_total(request.user.cliente)  # Usamos cliente recién creado o encontrado
                compra.comfimada = True
                compra.cliente= cliente
                compra.trabajador = request.user.trabajador
                compra.save()

        else:
            # Si no es un usuario staff, usa el cliente asociado al usuario logueado
            cliente = request.user.cliente
            if compra:
                compra.total = calcular_total(cliente)
                compra.comfimada = True
                compra.save()

        # Crear el envío solo si no es staff
        if not request.user.is_staff:
            envionew = Envio.objects.create(
                direccion=direccion,
                telefono=telefono,
                tarifa_envio=0,
                compra=compra,
                peso=0,
                repartidor=None
            )
        if request.user.is_staff:
            return HttpResponseRedirect(reverse("prods"))
        return HttpResponseRedirect(reverse("index"))


######################################################
def carrito(request):
    cliente_id = request.user.id ### no se usa borrar despues
    try:
        cliente = Cliente.objects.get(user=request.user)
    except Cliente.DoesNotExist:
        cliente = Trabajador.objects.get(user=request.user)

    compra_no_confirmada = Compra.objects.filter(trabajador=cliente, comfimada=False).first()

    if compra_no_confirmada:
        detalles = DetalleCompra.objects.filter(compra=compra_no_confirmada)
    else:
        detalles = []  

    if request.user.is_staff:
        return render(request, "plus/administracion/carrito.html", {
        "detalles": detalles
        })

    return render(request, "plus/cliente/carrito.html", {
        "detalles": detalles
    })

######################################################
def productos(request, id):
    producto = Producto.objects.get(pk=id)
    if request.user.is_staff:
        return render(request, "plus/administracion/articulo.html", {
        "producto": producto 
    })

    return render(request, "plus/cliente/productos.html", {
        "producto": producto 
    })

######################################################

def calcular_total(cliente_id):
    compra_no_confirmada = Compra.objects.filter(cliente_id=cliente_id, comfimada=False).first()

    if not compra_no_confirmada:
        return 0  

    detalles = DetalleCompra.objects.filter(compra=compra_no_confirmada)
    
    total = 0
    for detalle in detalles:
        total += detalle.producto.precio * detalle.cantidad

    return total
