import time
from collections import deque
from producto import Producto
from cliente import Cliente
from cajero import Cajero

def main():
    print(" === INICIANDO SIMULACIÓN KRUSTY KRAB   === \n")

    menu_carls = [
        Producto("Cangreburger", 90.00),
        Producto("Papas Fritas Bob Esponja", 45.50),
        Producto("Batido Kelp", 30.00),
        Producto("Malteada Marina", 55.00)]

    cola_autos = deque()

    pila_tickets_finalizados = []

    nombres_clientes = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]

    for nombre in nombres_clientes:
        cliente = Cliente(nombre)
        cola_autos.append(cliente)

    print(f"Hay {len(cola_autos)} autos formados en el Drive-Thru.\n")

    ventanilla1 = Cajero("VENTANILLA 1", cola_autos, menu_carls, pila_tickets_finalizados)
    ventanilla2 = Cajero("VENTANILLA 2", cola_autos, menu_carls, pila_tickets_finalizados)

    ventanilla1.start()
    ventanilla2.start()

    ventanilla1.join()
    ventanilla2.join()

    print("\n===============================================")
    print(" CORTE DE CAJA ")
    print("===============================================")
    
    total_dinero = 0.0
    
    while True:
        if (len(pila_tickets_finalizados) > 0):
            ticket = pila_tickets_finalizados.pop()
            print(f"Revisando ticket de {ticket.nombre} --- Total: ${ticket.total:.2f}")
            total_dinero += ticket.total
            time.sleep(0.3)
        else:
            break
            
    print("========================================")
    print(f"VENTA TOTAL DEL TURNO: ${total_dinero:.2f}")
    print("========================================")

if __name__ == "__main__":
    main()
