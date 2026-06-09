# app.py
import streamlit as st
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- RECONFIGURACIÓN DEL CAJERO PARA EL FRONTEND ---
# Modificamos ligeramente tu clase Cajero para que guarde variables que la pantalla pueda leer
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
                # Sacamos al cliente de la cola de forma segura
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Turno Finalizado"
                break

            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"🍔 Tomando orden de {cliente.nombre}"
        self.progreso = 10
        
        # Simulación de pedido aleatorio (Tu lógica exacta)
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        # Simulación del tiempo de preparación con barra de carga
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 Cocinando pedido de {cliente.nombre}..."
        
        # Dividimos el tiempo para animar la barra de progreso en la pantalla
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9) # Va subiendo hasta el 100%

        if (cliente.total > 0):
            self.estado = f"✅ ¡Orden Entregada a {cliente.nombre}!"
            self.pila_tickets.append(cliente)
            time.sleep(1.5) # Pausa para que el usuario alcance a ver el éxito
            
        self.cliente_actual = None
        self.estado = "☕ Esperando auto..."
        self.progreso = 0

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Drive-Thru Simulación")
st.markdown("**Proyecto de Estructuras de Datos & Programación Concurrente (Hilos)**")
st.write("---")

# 1. Definición del Menú (Tu lógica de Backend)
if 'menu' not in st.session_state:
    st.session_state.menu = [
        Producto("Hamburguesa Clásica", 90.00),
        Producto("Papas Fritas Grandes", 45.50),
        Producto("Refresco de Cola", 30.00),
        Producto("Malteada de Vainilla", 55.00)
    ]

# 2. Inicialización de los estados de la aplicación
if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

# --- BOTÓN DE DISPARO ---
if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Emulación de Drive-Thru", type="primary", use_container_width=True):
        nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        st.session_state.pila_tickets = []
        st.session_state.simulacion_activa = True
        st.rerun()

# --- MIENTRAS LA SIMULACIÓN ESTÉ CORRIENDO ---
if st.session_state.simulacion_activa:
    
    # Creamos e iniciamos los hilos de los cajeros de fondo (Solo la primera vez)
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    # Layout visual de la página web
    col_izquierda, col_derecha = st.columns([2, 1])

    with col_izquierda:
        st.subheader("🏪 Ventanillas de Atención en Paralelo")
        v_col1, v_col2 = st.columns(2)
        
        # Creamos contenedores vacíos para refrescarlos dinámicamente con un ciclo
        box_v1 = v_col1.empty()
        box_v2 = v_col2.empty()
        
        st.subheader("🚗 Fila de Autos Esperando (Cola - FIFO)")
        box_cola = st.empty()

    with col_derecha:
        st.subheader("🧾 Tickets Procesados (Pila - LIFO)")
        box_pila = st.empty()
        
        st.subheader("💰 Corte de Caja General")
        box_caja = st.empty()

    # CICLO DE REFRESCO DE LA PANTALLA (Refresca cada 0.3 segundos mientras los hilos trabajen)
    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        
        # Ventanilla 1 Visual
        with box_v1.container(border=True):
            st.markdown(f"### 🪟 {st.session_state.v1.nombre_cajero}")
            st.info(st.session_state.v1.estado)
            st.progress(st.session_state.v1.progreso)
            if st.session_state.v1.cliente_actual:
                st.caption(f"Cliente: **{st.session_state.v1.cliente_actual.nombre}**")

        # Ventanilla 2 Visual
        with box_v2.container(border=True):
            st.markdown(f"### 🪟 {st.session_state.v2.nombre_cajero}")
            st.info(st.session_state.v2.estado)
            st.progress(st.session_state.v2.progreso)
            if st.session_state.v2.cliente_actual:
                st.caption(f"Cliente: **{st.session_state.v2.cliente_actual.nombre}**")

        # Cola de Autos Visual
        autos_restantes = [c.nombre for c in st.session_state.cola_autos]
        if autos_restantes:
            box_cola.success(" ──> ".join([f"🚗 [{a}]" for a in autos_restantes]))
        else:
            box_cola.warning("Empty Drive-Thru: Ya no hay más autos en la fila.")

        # Pila de Tickets (Se muestran al revés, simulando que el último queda arriba)
        tickets_impresos = list(st.session_state.pila_tickets)
        if tickets_impresos:
            with box_pila.container():
                for tk in reversed(tickets_impresos):
                    st.text(f"📌 Ticket: {tk.nombre} - ${tk.total:.2f}")
        else:
            box_pila.caption("Esperando primer cierre...")

        # Conteo de Caja en Vivo
        dinero_actual = sum(tk.total for tk in tickets_impresos)
        box_caja.metric(label="Venta acumulada", value=f"${dinero_actual:.2f}")
        
        time.sleep(0.3) # Ritmo de actualización de la pantalla

    # --- CUANDO LOS HILOS TERMINAN ---
    st.session_state.simulacion_activa = False
    st.balloons() # Animación de festejo de Streamlit por terminar el turno
    st.success("🎉 ¡Simulación finalizada con éxito! Todos los clientes fueron atendidos.")