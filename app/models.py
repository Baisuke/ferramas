from django.db import models

# Create your models here.
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
    img = models.ImageField(upload_to='productos',null=True)

    def __str__(self):
        return self.cod_producto