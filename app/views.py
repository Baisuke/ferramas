from audioop import reverse
from datetime import datetime
from django.http import HttpResponse
from http.client import HTTPResponse
from django.shortcuts import render, redirect ,  get_object_or_404
from app.carrito import Carrito
from .models import Producto, Pedidos, ProductoPedido
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, authenticate, login
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.core.paginator import Paginator
import bcchapi
from django.shortcuts import render
from .models import Pedidos
from django.shortcuts import render, redirect
from .models import Pedidos
from transbank.webpay.webpay_plus.transaction import Transaction,WebpayOptions
from transbank.common.integration_type import IntegrationType
from django.urls import reverse

CommerCode = '597055555532'
ApiKeySecret = '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C'
options = WebpayOptions(CommerCode,ApiKeySecret,IntegrationType.TEST)
transaction = Transaction(options)


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
    pedidos = Pedidos.objects.filter(cliente=request.user)
    siete = bcchapi.Siete(file="credenciales.txt")
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    series_monedas = {
        "dolar": "F073.TCO.PRE.Z.D",
        "euro": "F072.CLP.EUR.N.O.D", 
        "libra": "F072.CLP.GBP.N.O.D",  
        "yen": "F072.CLP.JPY.N.O.D" 
    }

    valores_monedas = {}


    for moneda, serie in series_monedas.items():
        try:
            retcuadro = siete.cuadro(series=[serie], nombres=[moneda], desde=fecha_actual, hasta=fecha_actual)
            valor_moneda = retcuadro.iloc[0, 0]
            print(f"Valor del {moneda}: {valor_moneda}")

            if valor_moneda is None or valor_moneda <= 0:
                raise ValueError(f"El valor de {moneda} no es válido.")
            
            valores_monedas[moneda] = valor_moneda
        except Exception as e:
            print(f"Error al obtener el valor de {moneda}: {e}")
            valores_monedas[moneda] = 1 

    for pedido in pedidos:
        pedido.total_en_dolares = pedido.total / valores_monedas["dolar"]
        pedido.total_en_euros = pedido.total / valores_monedas["euro"]
        pedido.total_en_libras = pedido.total / valores_monedas["libra"]
        pedido.total_en_yenes = pedido.total / valores_monedas["yen"]

    moneda_seleccionada = request.POST.get('moneda', 'dolar') 
    if moneda_seleccionada in valores_monedas:
        for pedido in pedidos:
            total_convertido = pedido.total / valores_monedas[moneda_seleccionada]
            pedido.total_convertido = total_convertido
            pedido.moneda_seleccionada = moneda_seleccionada

    return render(request, 'app/mis_pedidos.html', {'pedidos': pedidos, 'valores_monedas': valores_monedas})



@permission_required('app.change_pedidos')
def listar_pedidos(request):

    pedidos = Pedidos.objects.all()

    for pedido in pedidos:
        pedido.productos = ProductoPedido.objects.filter(pedido=pedido)

    return render(request, 'app/listar_pedidos.html', {'pedidos': pedidos})


@permission_required('app.change_pedidos')
def confirmar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    pedido.estado = 'aceptado' 
    pedido.save()
    return redirect('listar_pedidos')

@permission_required('app.change_pedidos')
def rechazar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    pedido.estado = 'rechazado'
    pedido.save()
    return redirect('listar_pedidos')

@login_required
def pagar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    

    return render(request, 'app/pagar_pedido.html', {'pedido': pedido})

@login_required
def perfil_usuario(request):
    user = request.user
    if not user.is_staff:
        pedidos_aceptados = Pedidos.objects.filter(cliente=user, estado='aceptado').count()
        pedidos_pagados = Pedidos.objects.filter(cliente=user, estado='pagado').count()
        
        context = {
            'nombre': user.get_full_name(),
            'correo': user.email,
            'pedidos_aceptados': pedidos_aceptados,
            'pedidos_pagados': pedidos_pagados,
            'es_staff': False
        }
    else:
        context = {
            'nombre': user.get_full_name(),
            'correo': user.email,
            'rol': user.groups.first().name if user.groups.exists() else 'Sin rol asignado',
            'es_staff': True
        }
    
    return render(request, 'app/perfil_usuario.html', context)



@login_required
def pagar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedidos, id=pedido_id)
    transaction = Transaction(options)

    try:
        # Crear la transacción con la URL de retorno correcta
        response = transaction.create(
            buy_order=str(pedido.id),
            session_id=request.session.session_key,
            amount=pedido.total,
            return_url=request.build_absolute_uri(reverse('pago_exitoso'))  # Asegúrate de usar reverse
        )

        # Imprimir la URL para verificar
        print(f"Redirecting to: {response['url']}?token_ws={response['token']}")
        return redirect(f"{response['url']}?token_ws={response['token']}")
    except Exception as e:
        print(f"Error al crear la transacción: {e}")
        messages.error(request, "Ocurrió un error al procesar el pago. Por favor, inténtelo de nuevo.")
        return redirect('mis_pedidos')
    

@login_required
def pago_exitoso(request):
    token_ws = request.GET.get('token_ws')  # Obtener el token de la URL
    transaction = Transaction(options)  # Asegúrate de que 'options' esté definido
    result = transaction.commit(token_ws)  # Realiza la transacción con el token

    if result['status'] == 'AUTHORIZED':
        # Aquí se supone que el ID del pedido está en 'buy_order'
        pedido_id = int(result['buy_order'])  # Convierte a entero
        pedido = get_object_or_404(Pedidos, id=pedido_id)  # Obtiene el pedido basado en el ID
        pedido.estado = 'pagado'  # Asumiendo que el campo se llama 'estado'
        pedido.save()
        # Renderiza la plantilla con el pedido
        return render(request, 'app/pago_exitoso.html', {'pedido': pedido})
    else:
        return render(request, 'app/pago_fallido.html')  # Si no está autorizado, redirige a la página de error



