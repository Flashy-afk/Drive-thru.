class Producto:
    def __init__(self, nombre, precio):
        self._nombre = nombre
        self._precio = precio

    @property
    def nombre(self):
        return self._nombre
    
    @property
    def precio(self):
        return self._precio