import threading
import random
import time

class Cajero(threading.Thread):
    def __init__(self, nombre_cajero, cola_clientes, menu_restaurante, pila_tickets):
        super().__init__()
        self.nombre_cajero = nombre_cajero
        self.cola_clientes = cola_clientes
        self.menu = menu_restaurante
        self.pila_tickets = pila_tickets

    def run(self):
        while True:
            try:
                cliente = self.cola_clientes.popleft()
            except IndexError:
                print(f"\n[{self.nombre_cajero}] No hay mas autos, terminando turno.")
                break

            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        print(f"\n{self.nombre_cajero} está tomando la orden de {cliente.nombre}......")
        
        cantidad_productos = random.randint(1, 3)
        
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        tiempo_preparacion = random.randint(2, 5)
        time.sleep(tiempo_preparacion)

        if (cliente.total > 0):
            print(f"> {self.nombre_cajero} entrego la orden a {cliente.nombre} (Total: ${cliente.total:.2f})")
            
            self.pila_tickets.append(cliente)