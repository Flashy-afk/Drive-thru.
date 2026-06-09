# app.py
import streamlit as st
import streamlit.components.v1 as components
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- HILO 1: VENTANILLA DE ORDEN (ENTRADA / V2) ---
class VentanillaOrden(threading.Thread):
    def __init__(self, cola_clientes, cola_cocina, menu_restaurante):
        super().__init__()
        self.cola_clientes = cola_clientes
        self.cola_cocina = cola_cocina
        self.menu = menu_restaurante
        self.estado = "☕ Esperando..."
        self.cliente_actual = None

    def run(self):
        while True:
            try:
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Finalizado"
                break

            self.cliente_actual = cliente
            self.estado = "🍔 Ordenando..."
            time.sleep(2.5) # Tiempo estático para simular la toma del pedido
            
            # Selección de productos aleatorios
            cantidad_productos = random.randint(1, 3)
            for _ in range(cantidad_productos):
                producto_elegido = random.choice(self.menu)
                cliente.agregar_producto(producto_elegido)
            
            # Al terminar, el auto se mueve a la cola de la zona de cocina/entrega
            self.cola_cocina.append(cliente)
            self.cliente_actual = None
            self.estado = "☕ Esperando..."
        
        self.estado = "🔴 Finalizado"

# --- HILO 2: VENTANILLA DE ENTREGA Y COCINA (SALIDA / V1) ---
class VentanillaEntrega(threading.Thread):
    def __init__(self, cola_cocina, pila_tickets, thread_orden):
        super().__init__()
        self.cola_cocina = cola_cocina
        self.pila_tickets = pila_tickets
        self.thread_orden = thread_orden
        self.estado = "☕ Esperando..."
        self.cliente_actual = None
        self.progreso = 0

    def run(self):
        # Sigue operando si la ventanilla de orden sigue activa o si quedan autos por procesar en la cocina
        while (self.thread_orden.is_alive() or len(self.cola_cocina) > 0):
            try:
                cliente = self.cola_cocina.popleft()
            except IndexError:
                self.estado = "☕ Esperando..."
                time.sleep(0.2)
                continue

            self.cliente_actual = cliente
            
            # 1. Proceso de preparación ralentizado
            tiempo_preparacion = random.randint(4, 7)
            self.estado = "🍳 Cocinando..."
            for i in range(10):
                time.sleep(tiempo_preparacion / 10)
                self.progreso = (i + 1) * 10
            
            # 2. Proceso de pago y entrega en ventanilla final
            if (cliente.total > 0):
                self.estado = f"✅ Listo ${cliente.total:.0f}"
                self.pila_tickets.append(cliente)
                time.sleep(3.0) # Tiempo para apreciar quién se retira
            
            self.cliente_actual = None
            self.progreso = 0
            
        self.estado = "🔴 Finalizado"

# --- CONFIGURACIÓN DE LA INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Sequential Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Simulación Drive-Thru en Flujo Secuencial")
st.write("Visualización con división de procesos: Orden en Ventanilla 2 (Fondo) y Entrega en Ventanilla 1 (Frente).")
st.write("---")

if ('menu' not in st.session_state):
    st.session_state.menu = [
        Producto("Hamburguesa Clásica", 90.00),
        Producto("Papas Fritas Grandes", 45.50),
        Producto("Refresco de Cola", 30.00),
        Producto("Malteada de Vainilla", 55.00)
    ]

if ('simulacion_activa' not in st.session_state):
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.cola_cocina = deque()
    st.session_state.pila_tickets = []

col_btn, col_info = st.columns([1, 2])
with col_btn:
    if (not st.session_state.simulacion_activa):
        if (st.button("🚀 Iniciar Flujo de Procesos", type="primary", use_container_width=True)):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.cola_cocina = deque()
            st.session_state.pila_tickets = []
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if ('v2' not in st.session_state or not st.session_state.v2.is_alive()):
        # Instanciar hilos encadenados de forma secuencial
        st.session_state.v2 = VentanillaOrden(st.session_state.cola_autos, st.session_state.cola_cocina, st.session_state.menu)
        st.session_state.v1 = VentanillaEntrega(st.session_state.cola_cocina, st.session_state.pila_tickets, st.session_state.v2)
        st.session_state.v2.start()
        st.session_state.v1.start()

    col_mapa, col_reporte = st.columns([5, 3])

    with col_mapa:
        contenedor_mapa_vivo = st.empty()

    with col_reporte:
        st.subheader("🧾 Historial de Caja (Pila - LIFO)")
        box_pila = st.empty()
        box_caja = st.empty()

    # --- RENDERIZADO DEL MAPA EN TIEMPO REAL ---
    while (st.session_state.v1.is_alive() or st.session_state.v2.is_alive()):
        
        svg_mapa = """
        <svg width="100%" height="480" viewBox="0 0 800 480" style="background-color:#2c6b3f; border-radius:15px; font-family: sans-serif; box-shadow: inset 0 0 40px rgba(0,0,0,0.3);">
            <path d="M 80,240 L 250,140 Q 420,50 580,120 L 610,180 L 580,240 L 460,330 L 280,410" fill="none" stroke="#2a2a2a" stroke-width="75" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M 80,240 L 250,140 Q 420,50 580,120 L 610,180 L 580,240 L 460,330 L 280,410" fill="none" stroke="#ffcc00" stroke-width="2" stroke-dasharray="8,6" stroke-linecap="round" stroke-linejoin="round"/>
            
            <g transform="translate(80, 80)"><rect x="-3" y="0" width="6" height="20" fill="#5d4037"/><polygon points="0,-35 -18,-10 18,-10" fill="#1b5e20"/></g>
            <g transform="translate(710, 320)"><rect x="-3" y="0" width="6" height="20" fill="#5d4037"/><polygon points="0,-35 -18,-10 18,-10" fill="#1b5e20"/></g>

            <g transform="translate(110, 340)">
                <line x1="0" y1="0" x2="0" y2="60" stroke="#111" stroke-width="5"/>
                <rect x="-40" y="-35" width="80" height="35" rx="6" fill="#d32f2f" stroke="#fff" stroke-width="1.5"/>
                <text x="0" y="-12" fill="#ffcc00" font-size="22px" font-weight="bold" text-anchor="middle">★</text>
                <text x="0" y="-3" fill="#ffffff" font-size="7px" font-weight="bold" text-anchor="middle" letter-spacing="1">CARL'S JR.</text>
            </g>

            <polygon points="290,230 400,290 400,220 290,160" fill="#262626" stroke="#1a1a1a" stroke-width="0.5"/>
            <polygon points="400,290 510,220 510,150 400,220" fill="#404040" stroke="#1a1a1a" stroke-width="0.5"/>
            <text x="320" y="210" fill="#ffffff" font-size="12px" font-weight="bold" transform="rotate(25, 320, 210)">Carl's Jr.</text>

            <polygon points="420,210 445,194 445,235 420,251" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="412" y="185" fill="#ffffff" font-size="10px" font-weight="bold">V1: Entrega</text>
            
            <polygon points="465,181 490,165 490,206 465,222" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="478" y="150" fill="#ffffff" font-size="10px" font-weight="bold">V2: Orden</text>

            <polygon points="400,220 510,150 400,90 290,160" fill="#1c1c1c"/>
            <polygon points="400,220 510,150 400,90 290,160" fill="none" stroke="#ffcc00" stroke-width="3" stroke-linejoin="round"/>
        """

        # RUTA ENTRADA: PUNTOS ANTES DE LLEGAR A LA VENTANILLA DE ORDEN 2
        puntos_carril_entrada = [
            (575, 205), (570, 145), (515, 100), (425, 80), (330, 95), (245, 130), (175, 175)
        ]

        # 1. RENDER VEHÍCULO EN VENTANILLA 2 (ZONA DE ORDEN)
        if (st.session_state.v2.cliente_actual):
            svg_mapa += f"""
            <g transform="translate(525, 250)">
                <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-20,0 4,-11 22,-2 0,9" fill="#1976d2"/>
                <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#42a5f5"/>
                <rect x="-45" y="-30" width="90" height="16" rx="4" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v2.cliente_actual.nombre}</text>
                <text x="0" y="25" fill="#ffcc00" font-size="11px" font-weight="bold" text-anchor="middle">{st.session_state.v2.estado}</text>
            </g>
            """

        # 2. RENDER COLA INTERMEDIA (Autos que ya ordenaron y avanzan/esperan hacia la Ventanilla 1)
        for index, auto in enumerate(st.session_state.cola_cocina):
            if (index == 0 and not st.session_state.v1.cliente_actual):
                # Si el auto va en tránsito directo y V1 está libre, no se dibuja aquí para que pase directo a V1
                continue
            # Coordenada intermedia física entre V2 y V1 en la curva de la carretera
            cx_inter, cy_inter = 495, 280
            svg_mapa += f"""
            <g transform="translate({cx_inter}, {cy_inter})">
                <ellipse cx="0" cy="12" rx="22" ry="10" fill="rgba(0,0,0,0.3)"/>
                <polygon points="-18,0 4,-10 20,-2 0,8" fill="#e65100"/>
                <polygon points="-8,-4 4,-9 14,-5 2,1" fill="#ffb74d"/>
                <rect x="-45" y="-28" width="90" height="15" rx="3" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                <text x="0" y="24" fill="#ffb74d" font-size="9px" font-weight="bold" text-anchor="middle">En Espera V1</text>
            </g>
            """

        # 3. RENDER VEHÍCULO EN VENTANILLA 1 (ZONA DE COCINA / ENTREGA)
        if (st.session_state.v1.cliente_actual):
            svg_mapa += f"""
            <g transform="translate(460, 305)">
                <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-20,0 4,-11 22,-2 0,9" fill="#d32f2f"/>
                <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#ef5350"/>
                <rect x="-45" y="-30" width="90" height="16" rx="4" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v1.cliente_actual.nombre}</text>
                <text x="0" y="25" fill="#ffcc00" font-size="11px" font-weight="bold" text-anchor="middle">{st.session_state.v1.estado}</text>
            </g>
            """

        # 4. FILA DE ESPERA GENERAL (Hacia Ventanilla 2)
        for index, auto in enumerate(st.session_state.cola_autos):
            if (index < len(puntos_carril_entrada)):
                cx, cy = puntos_carril_entrada[index]
                svg_mapa += f"""
                <g transform="translate({cx}, {cy})">
                    <ellipse cx="0" cy="12" rx="22" ry="10" fill="rgba(0,0,0,0.3)"/>
                    <polygon points="-18,0 4,-10 20,-2 0,8" fill="#555555"/>
                    <polygon points="-8,-4 4,-9 14,-5 2,1" fill="#888888"/>
                    <rect x="-35" y="-28" width="70" height="15" rx="3" fill="rgba(0,0,0,0.8)"/>
                    <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                </g>
                """

        svg_mapa += "</svg>"
        
        with contenedor_mapa_vivo:
            components.html(svg_mapa, height=480)

        # RENDERIZADO DEL REPORTE HISTÓRICO DE TICKETS
        tickets_list = list(st.session_state.pila_tickets)
        with box_pila.container(border=True):
            if (tickets_list):
                for tk in reversed(tickets_list):
                    st.write(f"📌 **Ticket de {tk.nombre}** — Finalizado con ${tk.total:.2f}")
            else:
                st.caption("Esperando cierres en Ventanilla 1...")

        caja_total = sum(tk.total for tk in tickets_list)
        box_caja.metric(label="💰 Capital Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.25) # Suavizado del ciclo de render

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡El turno ha concluido! Todos los vehículos completaron la tubería secuencial de operaciones.")
