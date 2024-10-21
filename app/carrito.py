from app.models import Producto


class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito

    def add(self, producto):
        producto_id = str(producto.id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'imagen': producto.img.url,
                'nombre': producto.nombre,
                'acumulado': producto.precio,
                'producto_id': producto_id,
                'cantidad': 1
            }
        else:
            self.carrito[producto_id]['cantidad'] += 1

        self.session.modified = True


    def __iter__(self):
        for item_id in self.carrito:
            item = self.carrito[item_id]
            item['producto'] = Producto.objects.get(id=item_id)
            item['acumulado'] = item['cantidad'] * item['producto'].precio 
            yield item


    def eliminar(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar_carrito()

    def disminuir(self, producto):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]["cantidad"] -= 1
            if self.carrito[producto_id]["cantidad"] <= 0:
                self.eliminar(producto)
            else:
                # Actualizar 'acumulado' si la cantidad se mantiene
                self.carrito[producto_id]['acumulado'] = self.carrito[producto_id]['cantidad'] * producto.precio
                self.guardar_carrito()


    def limpiar(self):
        del self.session["carrito"]
        self.session.modified = True

    def guardar_carrito(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def total(self):
        return sum(item["producto"].precio * item["cantidad"] for item in self)

    def cantidad_total(self):
        return sum(item["cantidad"] for item in self)

    def to_dict(self):
        return {item_id: {"producto": item["producto"].id, "cantidad": item["cantidad"]} for item_id, item in self.carrito.items()}
