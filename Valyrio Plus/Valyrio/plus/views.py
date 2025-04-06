from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required ,user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum
from django.utils import timezone
from datetime import date       
from .models import *
from datetime import timedelta, datetime
from django.utils.timezone import now, make_aware

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
            return render(request, "plus/cliente/login.html", {
                "message": "Correo o contraseña invalida"
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
@login_required
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


def solicitudDevolucion(request, detalle_compra_id):
    if request.method == "POST":
        # Obtener los datos del formulario
        descripcion = request.POST.get("descripcion")
        imagen = request.FILES.get("imagen")
        
    
        
        
        
        if not imagen:
            messages.error(request, "Debe adjuntar una imagen para solicitar la devolución.")
            return redirect("solicitudDevolucion", detalle_compra_id)
        
        # Verificar si el detalle de compra existe y pertenece al cliente
        try:
            detalle_compra = DetalleCompra.objects.get(
                id=detalle_compra_id, compra__cliente=request.user.cliente
            )
        except DetalleCompra.DoesNotExist:
            messages.error(request, "El artículo seleccionado no es válido.")
            return redirect("solicitud_devolucion")
        
        # Crear la devolución para el detalle de compra
        devolucion = Devolucion(
            descripcion=descripcion,
            imagen=imagen,
            detalle_compra=detalle_compra,  # Asociar con el detalle de compra
            cliente=request.user.cliente,  # Asociar con el cliente
        )
        devolucion.save()

        messages.success(request, "Devolución solicitada exitosamente.")
        return redirect("perfil")  # Redirigir a una página de confirmación o listado

    # Aquí ya no necesitas usar `request.GET`, el ID de `detalle_compra` ya está disponible como argumento
    try:
        detalle_compra = DetalleCompra.objects.get(
            id=detalle_compra_id, compra__cliente=request.user.cliente
        )
        compras = [detalle_compra.compra]  # Solo la compra relacionada con el detalle
        detalles_por_compra = {
            detalle_compra.compra.id: [
                {
                    "id": detalle.id,
                    "producto": detalle.producto.nombre,
                    "cantidad": detalle.cantidad,
                }
                for detalle in DetalleCompra.objects.filter(compra=detalle_compra.compra)
            ]
        }
    except DetalleCompra.DoesNotExist:
        messages.error(request, "No se pudo encontrar el artículo o no es válido.")
        return redirect("solicitud_devolucion")

    return render(request, 'plus/cliente/Devolu.html', {
        'detalles_por_compra': detalles_por_compra,
        'detalle_compra': detalle_compra,  # Pasamos el detalle de compra al template
    })



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

        user = authenticate(request, username=username, password=password)
        #user = User.objects.get(username="Conde18")
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("prods"))
        else:
            return render(request, "plus/administracion/login.html", {
                "message": "Correo o contraseña invalida"
            })
    else:
        logout(request)
        return render(request, "plus/administracion/login.html")

######################################################

def Newrepartidor(request):
    if request.method =="POST":
        nombre = request.POST["nombre"]
        apellido = request.POST["apellido"]
        telefono = request.POST["telefono"]
        cedula = request.POST["cedula"]
        matricula = request.POST["matricula"]
        
        repartidor = Repartidor(
            nombre=nombre,
            apellido=apellido,
            telefono=telefono,
            cedula=cedula,
            matricula=matricula
        )
        repartidor.save()
        
    return render(request, "plus/administracion/Newrepartidor.html")

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
                password=contraseña,  # Almacenamos la contraseña de manera segura
                is_staff=True 
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
    

        cliente = request.user.trabajador
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
    registro = Compra.objects.filter(Cancelada= False)
    return render(request, "plus/administracion/compras.html", {
        "compras": registro,
        })

def comprasCanceladas(request):
    canceladas = Compra.objects.filter(Cancelada= True)
    envios = Envio.objects.filter(compra__in=canceladas)
    envios_por_compra = {envio.compra.id: envio.tarifa_envio for envio in envios}

    # Renderiza la plantilla con los datos
    return render(request, 'plus/administracion/ComprasConceladas.html', {
        'canceladas': canceladas,
        'envios_por_compra': envios_por_compra
    })



def compraEspecifica(request, id):
    compra = Compra.objects.get(id=id)
    detalles = DetalleCompra.objects.filter(compra=compra)
    metodo_pago = compra.metodo_pago

    # Convertir fecha_compra en datetime con zona horaria
    if isinstance(compra.fecha_compra, datetime):
        fecha_compra = compra.fecha_compra  # Ya es datetime
    else:
        fecha_compra = datetime.combine(compra.fecha_compra, datetime.min.time())

    # Hacer que fecha_compra sea "aware" (con zona horaria)
    fecha_compra = make_aware(fecha_compra)

    # Calcular el tiempo límite
    tiempo_limite = fecha_compra + timedelta(hours=48)
    dentro_de_48_horas = now() <= tiempo_limite  # Ahora ambas fechas son comparables

    # Verificar si existe un envío asociado a la compra
    envio = Envio.objects.filter(compra=compra).first()

    # Pasar las variables al contexto
    context = {
        'compra': compra,
        'detalles': detalles,
        'metodo_pago': metodo_pago,
        'dentro_de_48_horas': dentro_de_48_horas
    }

    # Solo agregar 'envio' si existe un envío
    if envio:
        context['envio'] = envio

    if not request.user.is_staff:
        return render(request, 'plus/cliente/ComEspe.html', context)
    return render(request, 'plus/administracion/ComEspe.html', context)

@staff_required
def devolucion(request):
    devoluciones_confirmadas = Devolucion.objects.filter(aceptada=True)
    devoluciones_no_confirmadas = Devolucion.objects.filter(aceptada=False)
    return render(request, "plus/administracion/devoluciones.html", {
        "devoluciones_confirmadas": devoluciones_confirmadas,
        "devoluciones_no_confirmadas": devoluciones_no_confirmadas
    })

@staff_required
def aceptarDevolucion(request, id):
    if request.method == 'POST':
        # Obtener la devolución mediante el ID
        dev = get_object_or_404(Devolucion, pk=id)
        # Cambiar el estado de la devolución a aceptada
        dev.aceptada = True
        dev.save()
        # Redirigir a la página de devoluciones (o a la página que desees)
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
        beneficiado = request.POST['beneficiado']
        justificacion = request.POST['justificacion']
        producto = Producto.objects.get(pk=request.POST['producto'])

        # Crear la nueva instancia de Regalias
        Regalias.objects.create(
            cantidad=cantidad,
            monto_total=monto_total,
            beneficiado=beneficiado,
            justificacion=justificacion,
            producto=producto
        )
        return redirect('registro_regalias')  # Cambia 'success_page' al nombre de tu vista de éxito

    productos = Producto.objects.all()
    return render(request, 'plus/administracion/Newregalias.html', {'productos': productos})

@staff_required
def inversion(request):
    inversiones = InversionColeccion.objects.filter(confirmada = True)
    for inversion in inversiones:
        # Obtener los detalles asociados a esta inversión
        inversion.detalles = DetalleInversion.objects.filter(inversion_coleccion=inversion)
    return render(request, "plus/administracion/invesion.html",{
        'inversiones' : inversiones,
    })

@staff_required
def registro_inversion(request):
    productos = Producto.objects.all()
    inversion = InversionColeccion.objects.filter(confirmada = False)

    if request.method == 'POST':
        prod = request.POST.get("prod")
        cant = request.POST.get("cantidad")

        produc = get_object_or_404(Producto, id=prod)

        inver = InversionColeccion.objects.filter(confirmada = False).first()

        if inver:
            DetalleInversion.objects.create(
                inversion_coleccion = inver,
                producto = produc,
                cantidad = cant
            )
        else:
            newInver = InversionColeccion.objects.create(
                total_inversion = 0,
                confirmada = False
            )
            DetalleInversion.objects.create(
                inversion_coleccion = newInver, 
                producto = produc,
                cantidad = cant
            )
        return redirect('registro_inversion') 

    return render(request, 'plus/administracion/Newinversion.html', 
                  {'productos': productos, 
                   "Inver": inversion
                   })

@staff_required
def confirmar_inversion(request):
    if request.method == "POST":
        # Obtener la inversión no confirmada
        inversion = InversionColeccion.objects.filter(confirmada=False).first()

        if not inversion:
            messages.error(request, "No hay inversiones pendientes para confirmar.")
            return redirect("registro_inversion")

        # Calcular el monto total de la inversión
        total_inversion = request.POST.get("Total")
        inversion.total_inversion = total_inversion
        inversion.confirmada = True
        inversion.save()

        # Actualizar las existencias de los productos
        for detalle in inversion.detalleinversion_set.all():
            producto = detalle.producto
            producto.cantidad += detalle.cantidad
            producto.save()

        messages.success(request, f"Inversión confirmada exitosamente con un total de {total_inversion} C$")
        return redirect("registro_inversion")
    
@staff_required    
def inversion_especifica(request, id):
    # Obtén la inversión específica
    inversion = get_object_or_404(InversionColeccion, id=id)
    detalles = inversion.detalleinversion_set.all()

    return render(request, 'plus/administracion/DetalleInversion.html', {
        'inversion': inversion,
        'detalles': detalles,
    })

@staff_required 
def cancelarCompra(request, id):
    com = Compra.objects.get(id=id) 
    com.Cancelada = True 
    com.total = 0
    com.save()

    return redirect(compras)

@staff_required

def ver_ganancias(request):
    # Calcular las ganancias para cada mes
    ganancias = []

    # Obtener las inversiones agrupadas por mes y año
    inversiones_mensuales = InversionColeccion.objects.annotate(
        mes=ExtractMonth('fecha_inversion'),
        anio=ExtractYear('fecha_inversion')
    ).values('mes', 'anio').annotate(total_inversion=Sum('total_inversion'))

    # Obtener las compras confirmadas agrupadas por mes y año
    compras_mensuales = Compra.objects.filter(comfimada=True).annotate(
        mes=ExtractMonth('fecha_compra'),
        anio=ExtractYear('fecha_compra')
    ).values('mes', 'anio').annotate(total_compra=Sum('total'))

    # Convertir los datos de las compras a un formato más manejable
    compras_dict = {(compra['mes'], compra['anio']): compra['total_compra'] for compra in compras_mensuales}

    # Comparar inversiones y compras para calcular las ganancias
    for inv in inversiones_mensuales:
        mes = inv['mes']
        anio = inv['anio']
        total_inversion = inv['total_inversion']
        total_compra = compras_dict.get((mes, anio), 0)
        ganancia = total_compra - total_inversion

        ganancias.append({
            'mes': mes,
            'anio': anio,
            'inversion': total_inversion,
            'compra': total_compra,
            'ganancia': ganancia,
        })

    return render(request, 'plus/administracion/Ganancias.html', {
        'ganancias': ganancias,
    })

@staff_required
def crear_producto(request):
    if request.method == "POST":
        # Obtener los datos del formulario manualmente
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', 'Sin descripción')
        precio = request.POST.get('precio')
        peso = request.POST.get('peso')
        imagen = request.FILES.get('imagen')    
        
        # Crear un nuevo producto
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            cantidad=0,
            peso=peso,
            imagen=imagen
        )
        producto.save()
        return redirect('registro_inversion')  # Redirigir a la página que desees, por ejemplo, la lista de productos
    return render(request, 'plus/administracion/NewProd.html')
#----------------------------------------------------------Ambos--------------------------------------------------------------#
######################################################
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


######################################################
def realizar_compra(request):
    if request.method == "POST":
        # Filtrar los detalles de la compra
        if request.user.is_staff:
            detalles = DetalleCompra.objects.filter(compra__trabajador=request.user.trabajador, compra__comfimada=False)
        else:
            detalles = DetalleCompra.objects.filter(compra__cliente=request.user.cliente, compra__comfimada=False)

        # Calcular peso total y tarifa de envío solo para clientes
        if not request.user.is_staff:
            # Calcular peso total
            peso_total = calcular_peso_total(detalles)

            # Obtener destino del formulario
            destino = request.POST.get("destino")  # 'Managua', 'Rio San Juan', etc.

            # Calcular tarifa de envío
            tarifa_envio = calcular_tarifa_envio(peso_total, destino)

            if tarifa_envio is None:
                messages.error(request, "El peso de los productos excede el límite permitido.")
                return redirect("carrito")  # Redirige si no se puede calcular la tarifa
        else:
            peso_total = 0  # No se calcula para el staff
            tarifa_envio = 0  # No se calcula para el staff

        # Procesar detalles y actualizar cantidades
        for detalle in detalles:
            cantidad = request.POST.get(f"cantidad_{detalle.id}")
            if cantidad and cantidad.isdigit():
                cantidad = int(cantidad)
                if cantidad > detalle.producto.cantidad or cantidad <= 0:
                    messages.error(
                        request,
                        f"El producto '{detalle.producto.nombre}' solo tiene {detalle.producto.cantidad} existencias."
                    )
                    return redirect("carrito")  # Redirige al carrito si hay un error
                detalle.cantidad = cantidad
                detalle.save()
                producto = detalle.producto
                producto.cantidad -= cantidad
                producto.save()

        # Obtener o crear la compra
        if request.user.is_staff:
            compra = Compra.objects.filter(trabajador=request.user.trabajador, comfimada=False).first()
        else:
            compra = Compra.objects.filter(cliente=request.user.cliente, comfimada=False).first()

        # Verificar o crear cliente
        if request.user.is_staff:
            tipo_usuario = request.POST.get("tipo_usuario")
            if tipo_usuario == "usuario":  # Cliente existente
                correo_cliente = request.POST.get("cliente")
                cliente = Cliente.objects.filter(correo=correo_cliente).first()
                compra.cliente = cliente
                compra.save()
                if not cliente:
                    messages.error(request, "El correo proporcionado no está registrado.")
                    return redirect("carrito")  # Redirige si no se encuentra el cliente
            elif tipo_usuario == "nuevo":  # Cliente sin cuenta
                nombre = request.POST.get("name")
                correo = request.POST.get("correo", "default@gmail.com")
                contraseña = request.POST.get("contraseña", "1234")
                
                # Crear un nuevo cliente y asignar el cliente a la compra
                usuario = User.objects.create_user(username=nombre, email=correo, password=contraseña)
                cliente = Cliente.objects.create(
                    user=usuario,
                    nombre=nombre,
                    apellido="",
                    telefono=000000,
                    cedula=000000,
                    correo=correo,
                    contraseña=contraseña
                )

                # Asociar cliente a la compra
                compra.cliente = cliente
                compra.save()

        # Obtener el método de pago seleccionado
        metodo_pago_id = request.POST.get("tipo_pago")  # Suponiendo que se envía el ID del metodo_pago
        print(metodo_pago_id)
        metodo_pago = MetodoPago.objects.filter(id=metodo_pago_id).first() 
        print(metodo_pago) # Obtener el objeto MetodoPago
        imagen_comprobante = request.FILES.get('imagen_pago')   
        print(imagen_comprobante)
        if metodo_pago:
            # Asignar el método de pago a la compra
            
            compra.metodo_pago = metodo_pago
            
        if imagen_comprobante: 
            compra.comprobante = imagen_comprobante
        # Confirmar compra
        if compra:
            compra.fecha_compra = date.today()
            compra.total = sum(detalle.producto.precio * detalle.cantidad for detalle in detalles)  # Calcula el total
            compra.comfimada = True
            compra.save()

        # Crear envío solo para clientes
        if not request.user.is_staff:
            Envio.objects.create(
                direccion=request.POST.get("direccion"),
                telefono=request.POST.get("telefono"),
                tarifa_envio=tarifa_envio,
                peso=peso_total,
                compra=compra,
            )

        messages.success(request, f"Compra realizada con éxito. Tarifa de envío: {tarifa_envio} C$")
        if request.user.is_staff:
            return redirect('prods')
        return HttpResponseRedirect(reverse("index"))


######################################################
def carrito(request):
    cliente_id = request.user.id ### no se usa borrar despues
    try:
        if request.user.is_staff:
            cliente = Cliente.objects.get(user=request.user)
        else:
            cliente = request.user.cliente 

    except Cliente.DoesNotExist:
        cliente = Trabajador.objects.get(user=request.user)

    if request.user.is_staff:
        compra_no_confirmada = Compra.objects.filter(trabajador=cliente, comfimada=False).first()
    else:
        compra_no_confirmada = Compra.objects.filter(cliente=cliente, comfimada=False).first()

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

def calcular_total(user):
    if user.user.is_staff:
        compra_no_confirmada = Compra.objects.filter(trabajador=user, comfimada=False).first()
    else:
        compra_no_confirmada = Compra.objects.filter(cliente=user, comfimada=False).first()

    if not compra_no_confirmada:
        return 0  
    detalles = DetalleCompra.objects.filter(compra=compra_no_confirmada)
    
    total = 0
    for detalle in detalles:
        total += detalle.producto.precio * detalle.cantidad

    return total

######################################################
def calcular_peso_total(detalles):
    """Calcula el peso total de los productos en el carrito."""
    peso_total = 0
    for detalle in detalles:
        peso_total += detalle.producto.peso * detalle.cantidad
    return peso_total

######################################################
def calcular_tarifa_envio(peso_total, destino):
    """Determina la tarifa de envío según el peso total y el destino."""
    tarifas = {
        "Managua": [(11, 100), (22, 180), (33, 220)],
        "Rio San Juan": [(11, 400), (22, 450), (33, 510)],
        "Bluefields": [(11, 210), (22, 560), (33, 925)],
        "Puerto Cabezas": [(11, 210), (22, 560), (33, 925)],
        "Resto departamentos": [(11, 130), (22, 220), (33, 275)],
    }

    for limite_peso, tarifa in tarifas[destino]:
        if peso_total <= limite_peso:
            return tarifa

    return None