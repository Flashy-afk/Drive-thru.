import streamlit as st
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- RECONFIGURACIÓN DEL CAJERO PARA EL FRONTEND ---
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
        self.estado = f"🍔 Tomando orden de {cliente.nombre}"
        self.progreso = 10
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
        
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 Cocinando pedido de {cliente.nombre}..."
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9)

        if (cliente.total > 0):
            self.estado = f"✅ ¡Orden Entregada a {cliente.nombre}!"
            self.pila_tickets.append(cliente)
            time.sleep(1.5)
            
        self.cliente_actual = None
        self.estado = "☕ Esperando auto..."
        self.progreso = 0

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Carl's Jr. Drive-Thru", page_icon="🍔", layout="wide")
st.title("🍔 Carl's Jr. — Drive-Thru Simulación")
st.markdown("**Flujo del Sistema: Fila ➔ Preparación ➔ Caja**")
st.write("---")

if 'menu' not in st.session_state:
    st.session_state.menu = [
        Producto("Hamburguesa Clásica", 90.00),
        Producto("Papas Fritas Grandes", 45.50),
        Producto("Refresco de Cola", 30.00),
        Producto("Malteada de Vainilla", 55.00)
    ]

if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Emulación de Drive-Thru", type="primary", use_container_width=True):
        nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        st.session_state.pila_tickets = []
        st.session_state.simulacion_activa = True
        st.rerun()

if st.session_state.simulacion_activa:
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    # --- DISEÑO DE 3 COLUMNAS ---
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.subheader("1. 🚗 Fila")
        box_cola = st.empty()

    with col2:
        st.subheader("2. 🍳 Cocina")
        v_col1, v_col2 = st.columns(2)
        box_v1 = v_col1.empty()
        box_v2 = v_col2.empty()

    with col3:
        st.subheader("3. 🧾 Caja")
        box_caja = st.empty()
        box_pila = st.container(height=300)

    # --- BUCLE DE ACTUALIZACIÓN ---
    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        
        # 1. Cola
        autos_restantes = [c.nombre for c in st.session_state.cola_autos]
        box_cola.write("\n\n".join([f"🚗 **{a}**" for a in autos_restantes]) if autos_restantes else "Vacío")

        # 2. Ventanillas
        def render_v(box, c):
            with box.container(border=True):
                st.caption(c.nombre_cajero)
                st.write(c.estado)
                st.progress(c.progreso / 100)
                if c.cliente_actual: st.caption(f"👤 {c.cliente_actual.nombre}")
        
        render_v(box_v1, st.session_state.v1)
        render_v(box_v2, st.session_state.v2)

        # 3. Caja
        tickets = list(st.session_state.pila_tickets)
        box_caja.metric("Venta total", f"${sum(tk.total for tk in tickets):.2f}")
        box_pila.empty()
        with box_pila:
            for tk in reversed(tickets):
                st.text(f"✅ {tk.nombre}: ${tk.total:.2f}")

        time.sleep(0.3)

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡Simulación finalizada!")
