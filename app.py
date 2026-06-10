import streamlit as st
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- CLASE CAJERO (Mantiene la lógica de hilos) ---
class CajeroVisual(threading.Thread):
    def __init__(self, nombre_cajero, cola_clientes, menu_restaurante, pila_tickets):
        super().__init__()
        self.nombre_cajero = nombre_cajero
        self.cola_clientes = cola_clientes
        self.menu = menu_restaurante
        self.pila_tickets = pila_tickets
        self.estado = "☕ Esperando..."
        self.cliente_actual = None
        self.progreso = 0

    def run(self):
        while True:
            try:
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Turno Finalizado"
                break
            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"🍔 Tomando pedido: {cliente.nombre}"
        self.progreso = 10
        for _ in range(random.randint(1, 3)):
            cliente.agregar_producto(random.choice(self.menu))
        
        tiempo = random.randint(2, 5)
        self.estado = f"🍳 Cocinando: {cliente.nombre}"
        for i in range(10):
            time.sleep(tiempo / 10)
            self.progreso = 10 + (i * 9)

        self.estado = f"✅ Pedido listo: {cliente.nombre}"
        self.pila_tickets.append(cliente)
        time.sleep(1)
        self.cliente_actual = None
        self.estado = "☕ Esperando..."
        self.progreso = 0

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Carl's Jr. Drive-Thru", layout="wide")
st.title("🍔 Circuito Drive-Thru: Carl's Jr.")

if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []
    st.session_state.menu = [Producto("Hamburguesa", 90.0), Producto("Papas", 45.5), Producto("Refresco", 30.0)]

if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Recorrido"):
        st.session_state.cola_autos = deque([Cliente(n) for n in ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]])
        st.session_state.simulacion_activa = True
        st.rerun()

# --- DISEÑO DINÁMICO ---
if st.session_state.simulacion_activa:
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    # Layout de "Circuito"
    st.markdown("### 🗺️ Circuito del Drive-Thru")
    
    # 1. Zona de Menú (Inicio)
    st.caption("Fase 1: Pedido")
    box_cola = st.empty()
    
    # 2. Zona de Atención (Medio - Ventanillas)
    c1, c2 = st.columns(2)
    box_v1 = c1.empty()
    box_v2 = c2.empty()
    
    # 3. Zona de Caja (Final)
    st.caption("Fase 2: Pago y Recolección")
    box_pila = st.empty()

    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        # Representación del flujo: 
        # Mostramos quienes están en la cola (esperando) y quienes están siendo atendidos (en ventanilla)
        
        # Fila de espera
        autos_esperando = [c.nombre for c in st.session_state.cola_autos]
        box_cola.info("Fila de espera: " + " ➔ ".join([f"🚗 {a}" for a in autos_esperando]))

        # Ventanillas (Movimiento al centro)
        def render_v(box, c):
            if c.cliente_actual:
                box.success(f"📍 ATENDIENDO A: 🚗 {c.cliente_actual.nombre} | Progreso: {c.progreso}%")
            else:
                box.write("Ventanilla Libre")
        
        render_v(box_v1, st.session_state.v1)
        render_v(box_v2, st.session_state.v2)

        # Caja
        tickets = list(st.session_state.pila_tickets)
        box_pila.write(f"🧾 Último cliente atendido: **{tickets[-1].nombre if tickets else 'Ninguno'}** | Venta Total: ${sum(tk.total for tk in tickets):.2f}")

        time.sleep(0.2) # Velocidad de la animación

    st.success("🎉 ¡Todos los autos completaron el circuito!")
    st.session_state.simulacion_activa = False
