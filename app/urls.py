from django.urls import path
from .views import agregar_producto, confirmar_pedido, eliminar_producto, home, limpiar_carrito, listar_pedidos, mis_pedidos, pagar_pedido, rechazar_pedido, restar_producto, pago, exit, register,realizar_pedido


urlpatterns = [
    path('', home, name="home"),
    path('agregar/<int:producto_id>/',agregar_producto, name="add"),
    path('eliminar/<int:producto_id>/',eliminar_producto, name="del"),
    path('restar/<int:producto_id>/',restar_producto, name="sub"),
    path('limpiar/',limpiar_carrito, name="cls"),
    path('pago/', pago, name='pago'),
    path('logout/',exit, name='exit'),
    path('register/',register, name='register'),
    path('realizar-pedido/', realizar_pedido, name='realizar_pedido'),
    path('pedidos/', listar_pedidos, name='listar_pedidos'),
    path('pedidos/confirmar/<int:pedido_id>/', confirmar_pedido, name='confirmar_pedido'),
    path('pedidos/rechazar/<int:pedido_id>/', rechazar_pedido, name='rechazar_pedido'),
    path('mis_pedidos/', mis_pedidos, name='mis_pedidos'),
    path('pagar_pedido/<int:pedido_id>/', pagar_pedido, name='pagar_pedido'),
]
