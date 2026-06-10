import streamlit as st
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- CLASE CAJERO (Mantiene tu lógica concurrente) ---
class CajeroVisual(threading.Thread):
    def __init__(self, nombre_cajero, cola_clientes, menu_restaurante, pila_tickets):
        super().__init__()
        self.nombre_cajero = nombre_cajero
        self.cola_clientes = cola_clientes
        self.menu = menu_restaurante
        self.pila_tickets = pila_tickets
        self.estado = "☕ Esperando auto..."
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
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            cliente.agregar_producto(random.choice(self.menu))
        
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 Cocinando para {cliente.nombre}..."
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9)

        if (cliente.total > 0):
            self.estado = f"✅ Pedido entregado a {cliente.nombre}"
            self.pila_tickets.append(cliente)
            time.sleep(1)
            
        self.cliente_actual = None
        self.estado = "☕ Esperando..."
        self.progreso = 0

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Carl's Jr. Drive-Thru", layout="wide")
st.title("🍔 Circuito Drive-Thru: Carl's Jr.")

if 'menu' not in st.session_state:
    st.session_state.menu = [Producto("Hamburguesa", 90.0), Producto("Papas", 45.5), Producto("Refresco", 30.0), Producto("Malteada", 55.0)]
if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Circuito"):
        st.session_state.cola_autos = deque([Cliente(n) for n in ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]])
        st.session_state.simulacion_activa = True
        st.rerun()

# --- DISEÑO DEL CIRCUITO ---
if st.session_state.simulacion_activa:
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    # Fila de Entrada (Zona de Pedido)
    st.subheader("1. 🗣️ Zona de Menú (Levantar pedido)")
    box_cola = st.empty()
    
    st.markdown("---")
    
    # Zona de Cocina/Caja (La vuelta del circuito)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.subheader("2. 🍳 Ventanilla 1")
        box_v1 = st.empty()
    with c2:
        st.subheader("3. 🍳 Ventanilla 2")
        box_v2 = st.empty()
    with c3:
        st.subheader("4. 💰 Caja / Salida")
        box_caja = st.empty()
        box_pila = st.container(height=250)

    # Bucle de actualización
    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        # Fila horizontal (Camino)
        autos = [c.nombre for c in st.session_state.cola_autos]
        box_cola.markdown("  ".join([f"🚗 **{a}**" for a in autos]))

        # Renderizar ventanillas
        def render_v(box, c):
            with box.container(border=True):
                st.write(c.estado)
                st.progress(c.progreso / 100)
                if c.cliente_actual: st.info(f"👤 {c.cliente_actual.nombre}")
        render_v(box_v1, st.session_state.v1)
        render_v(box_v2, st.session_state.v2)

        # Caja
        tickets = list(st.session_state.pila_tickets)
        box_caja.metric("Venta Total", f"${sum(tk.total for tk in tickets):.2f}")
        box_pila.empty()
        with box_pila:
            for tk in reversed(tickets):
                st.text(f"✅ {tk.nombre}: ${tk.total:.2f}")
        time.sleep(0.3)

    st.success("🎉 ¡Circuito finalizado!")
    st.session_state.simulacion_activa = False
