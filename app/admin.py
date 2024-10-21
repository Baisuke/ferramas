from django.contrib import admin
from .models import Categoria, Producto, Pedidos, ProductoPedido

# Register your models here.
admin.site.register(Categoria)
admin.site.register(Producto)

class ProductoPedidoInline(admin.TabularInline):
    model = ProductoPedido
    extra = 0

@admin.register(Pedidos)
class PedidosAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'total', 'fecha_pedido', 'productos_list')
    inlines = [ProductoPedidoInline]

    def productos_list(self, obj):
        return ", ".join([str(producto.producto) for producto in obj.productopedido_set.all()])
    productos_list.short_description = 'Productos'
