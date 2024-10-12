from django.shortcuts import render
from .models import Producto
from django.db.models import Q

def home(request):
    busqueda = request.GET.get("Buscar")  # Obtener el término de búsqueda
    productos = Producto.objects.all()
    filtro = request.GET.get("filtro")

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(cod_producto__icontains=busqueda)
        ).distinct()
    if filtro:
        productos = productos.filter(categoria=filtro)  # Cambia esto según tus campos

    data = {
        'productos': productos
    }
    return render(request, 'app/home.html', data)

    data = {
        'productos': productos
    }
    return render(request, 'app/home.html', data)
