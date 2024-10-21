def total_carrito(request):
    carrito = request.session.get('carrito', {})
    total = sum(float(item['acumulado']) * item['cantidad'] for item in carrito.values() if 'acumulado' in item)
    return {'total_carrito': total}

