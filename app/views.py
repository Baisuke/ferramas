from django.shortcuts import render, redirect ,  get_object_or_404
from app.carrito import Carrito
from .models import Producto, Pedidos, ProductoPedido
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, authenticate, login
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator

def home(request):
    busqueda = request.GET.get("Buscar") 
    productos = Producto.objects.all()
    filtro = request.GET.get("filtro")

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(marca__icontains=busqueda) |
            Q(cod_producto__icontains=busqueda)
        ).distinct()
    
    if filtro:
        productos = productos.filter(categoria=filtro)

    paginator = Paginator(productos, 8) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = {
        'productos': page_obj
    }
    
    return render(request, 'app/home.html', data) 


@login_required
def pago(request):
    carrito = Carrito(request)
    total = 0

    # Crear una lista para almacenar los productos del carrito
    productos_del_carrito = []

    for item in carrito:
        producto = item['producto'] 
        cantidad = item['cantidad']
        subtotal = producto.precio * cantidad
        total += subtotal
        
        productos_del_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    context = {
        'productos': productos_del_carrito,
        'total': total,
    }

    return render(request, 'app/pago.html', context)



def exit(request):
    logout(request)
    return redirect('home')

def register(request):
    data = {
        'form': CustomUserCreationForm
    }

    if request.method == 'POST':
        user_creation_form = CustomUserCreationForm(data=request.POST)

        if user_creation_form.is_valid():
            user_creation_form.save()
            user = authenticate(username=user_creation_form.cleaned_data['username'],password=user_creation_form.cleaned_data['password1'])
            login(request,user)
            messages.success(request, "¡Registro exitoso!")
            return redirect('home')
        else:
            messages.error(request, "Hubo un error en el registro. Por favor, revisa los datos.")
            data['form'] = user_creation_form
    return render(request,'registration/register.html',data)

def agregar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.add(producto) 
    next_url = request.GET.get('next', '/')
    return redirect(next_url)



def eliminar_producto(request,producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    next_url = request.GET.get('next', '/') 
    return redirect(next_url)

def restar_producto(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.disminuir(producto)
    return redirect("home")

def limpiar_carrito(request):
    carrito= Carrito(request)
    carrito.limpiar()
    return redirect("home")

@login_required
def realizar_pedido(request):
    if request.method == 'POST':
        carrito = Carrito(request)
        tipo_pago = request.POST.get('tipo_pago') 

        pedido = Pedidos.objects.create(cliente=request.user, tipo_pago=tipo_pago ,total=0)
        
        total_pedido = 0 

        for item in carrito:
            producto = Producto.objects.get(id=item['producto'].id)
            cantidad = item['cantidad']
            subtotal = producto.precio * cantidad
            

            ProductoPedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, total=subtotal)

            total_pedido += subtotal  


        pedido.total = total_pedido
        pedido.save()


        carrito.limpiar()

        messages.success(request, "¡Pedido realizado con éxito!")
        return redirect('home')  

    return render(request, 'app/pago.html')

@login_required
def mis_pedidos(request):
    # Obtener todos los pedidos del usuario actual
    pedidos = Pedidos.objects.filter(cliente=request.user)
    
    for pedido in pedidos:
        pedido.productos = ProductoPedido.objects.filter(pedido=pedido)

    return render(request, 'app/mis_pedidos.html', {'pedidos': pedidos})




@permission_required('app.change_pedidos')
def listar_pedidos(request):

    pedidos = Pedidos.objects.all()

    for pedido in pedidos:
        pedido.productos = ProductoPedido.objects.filter(pedido=pedido)

    return render(request, 'app/listar_pedidos.html', {'pedidos': pedidos})


@permission_required('app.change_pedidos')
def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    pedido.estado = 'aceptado'  # Actualiza el estado a aceptado
    pedido.save()
    return redirect('listar_pedidos')

@permission_required('app.change_pedidos')
def rechazar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    pedido.estado = 'rechazado'  # Actualiza el estado a rechazado
    pedido.save()
    return redirect('listar_pedidos')

@login_required
def pagar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    

    return render(request, 'app/pagar_pedido.html', {'pedido': pedido})
