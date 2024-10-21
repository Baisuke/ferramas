from django.db import models
from django.conf import settings
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    cod_producto = models.CharField(max_length=50)
    marca = models.CharField(max_length=50)
    nombre = models.CharField(max_length=50)
    precio = models.IntegerField()
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    fecha = models.DateField()
    img = models.ImageField(upload_to='productos', null=True)

    def __str__(self):
        return self.cod_producto

class Pedidos(models.Model):
    ESTADO_CHOICES = [
            ('pendiente', 'Pendiente'),
            ('aceptado', 'Aceptado'),
            ('rechazado', 'Rechazado'),
        ]
    fecha_pedido = models.DateField(auto_now_add=True) 
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.IntegerField()
    tipo_pago = models.CharField(max_length=50)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
   
    def __str__(self):
        return f'Pedido {self.id} de {self.cliente}'
    
    def __str__(self):
        return f"Pedido {self.id} - {self.estado}"

    def productos(self):
        return self.productopedido_set.all()

class ProductoPedido(models.Model):
    pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    total = models.IntegerField()
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return str(self.producto)

    def to_json(self):
        item = model_to_dict(self, exclude=['created'])
        return item
