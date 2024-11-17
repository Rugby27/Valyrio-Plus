from django.urls import path

from . import views

urlpatterns = [
    #-----------------Clientes-----------------------#
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("productos/<int:id>", views.productos, name="productos"),
    path("carrito", views.carrito,name="carrito"),
    path("agregarCarrito",views.agregarCarrito,name="agrecarrito"),
    path("realizarCompra",views.realizar_compra, name="Compra"),
    path("perfil",views.perfil,name="perfil"),
    
    #-----------------Admin-----------------------#
    path("loggin", views.login_traba, name="loggin"),
    path("registerr",views.register_traba,name="registerr"),
    path("trabajadores",views.trabajadores,name="trabajadores"),
    path("prods",views.prods,name="prods"),
    path('envios/', views.envios, name='envios'),
    path('envios/asignar_repartidor/<int:envio_id>/', views.asignar_repartidor, name='asignar_repartidor'),
    path('compraLocal',views.compraLocal,name="compraLocal"),
    path('compras',views.compras, name="compras"),
    path('devolucion',views.devolucion,name="devolucion"),
    path('aceptarDevolucion/<int:id>',views.aceptarDevolucion,name="aceptarDevolucion"),
    path('regalias',views.regalias,name="regalias"),
    path('registro-regalias/', views.registro_regalias, name='registro_regalias'),
    path('inversion',views.inversion,name="inversion"),
    path('registro_inversion',views.registro_inversion,name="registro_inversion"),

    #-----------------ambos-----------------------#
    path("logout", views.logout_view, name="logout"),

]