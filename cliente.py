from producto import Producto

class Cliente:
    def __init__(self, nombre):
        self._nombre = nombre
        self._carrito = []
        self._total = 0.0

    @property
    def nombre(self):
        return self._nombre

    @property
    def carrito(self):
        return self._carrito
        
    @property
    def total(self):
        return self._total

    def agregar_producto(self, producto:Producto):
        self._carrito.append(producto)
        self._total += producto.precio


