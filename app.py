# app.py
import streamlit as st
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- RECONFIGURACIÓN DEL CAJERO PARA EL MAPA VISUAL ---
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
                self.estado = "🔴 Finalizado"
                break

            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"🍔 Ordenando..."
        self.progreso = 10
        
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 Cocinando..."
        
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9)

        if (cliente.total > 0):
            self.estado = f"✅ Listo ${cliente.total:.0f}"
            self.pila_tickets.append(cliente)
            time.sleep(1.5) # Tiempo para ver el auto cobrar en la ventanilla
            
        self.cliente_actual = None
        self.estado = "☕ Esperando..."
        self.progreso = 0

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Carl's Jr. Isometric Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Simulación Drive-Thru en Perspectiva 3D")
st.write("Visualización isométrica en tiempo real del flujo vehicular utilizando hilos paralelos.")
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

col_btn, col_info = st.columns([1, 2])
with col_btn:
    if (not st.session_state.simulacion_activa):
        if st.button("🚀 Iniciar Simulación 3D", type="primary", use_container_width=True):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.pila_tickets = []
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    col_mapa, col_reporte = st.columns([5, 3])

    with col_mapa:
        contenedor_mapa_vivo = st.empty()

    with col_reporte:
        st.subheader("🧾 Historial de Caja (Pila - LIFO)")
        box_pila = st.empty()
        box_caja = st.empty()

    # --- RENDERIZADO DEL MAPA ISOMÉTRICO ---
    while (st.session_state.v1.is_alive() or st.session_state.v2.is_alive()):
        
        # DEFINICIÓN DEL GRÁFICO BASE: Terreno, Carretera de Asfalto y Árboles
        svg_mapa = """
        <svg width="100%" height="480" viewBox="0 0 800 480" style="background-color:#4caf50; border-radius:15px; box-shadow: inset 0 0 40px rgba(0,0,0,0.15);">
            <path d="M 180,-20 L 460,110 L 720,110 L 740,240 L 520,340 L 220,470 L 100,410 L 440,260 L 140,120 Z" fill="#424242"/>
            <path d="M 280,30 L 465,115 Q 580,115 630,160 L 460,240 L 230,345" fill="none" stroke="#555555" stroke-width="70" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M 280,30 L 465,115 Q 580,115 630,160 L 460,240 L 230,345" fill="none" stroke="#ffcc00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="10,8"/>
            
            <g transform="translate(100, 60)">
                <rect x="-3" y="0" width="6" height="25" fill="#5d4037"/>
                <polygon points="0,-45 -22,-15 0,5 22,-15" fill="#2e7d32"/>
                <polygon points="0,-55 -15,-30 0,-10 15,-30" fill="#388e3c"/>
            </g>
            <g transform="translate(720, 360)">
                <rect x="-3" y="0" width="6" height="25" fill="#5d4037"/>
                <polygon points="0,-45 -22,-15 0,5 22,-15" fill="#2e7d32"/>
            </g>

            <g transform="translate(140, 240)">
                <line x1="0" y1="0" x2="0" y2="70" stroke="#333333" stroke-width="5"/>
                <rect x="-35" y="-35" width="70" height="35" rx="5" fill="#d32f2f" stroke="#fff" stroke-width="2"/>
                <text x="0" y="-18" fill="#ffcc00" font-size="22px" font-weight="bold" text-anchor="middle">★</text>
                <text x="0" y="-4" fill="#ffffff" font-size="8px" font-weight="bold" text-anchor="middle" font-family="sans-serif">DRIVE THRU</text>
            </g>

            <polygon points="360,140 490,200 360,260 230,200" fill="#1a1a1a" stroke="#222" stroke-width="1"/>
            <polygon points="230,200 360,260 360,340 230,280" fill="#2d2d2d"/>
            <polygon points="360,260 490,200 490,280 360,340" fill="#3a3a3a"/>
            <polygon points="360,145 490,205 490,212 360,252" fill="none" stroke="#ffcc00" stroke-width="4"/>
            <polygon points="230,205 360,252 360,259 230,212" fill="none" stroke="#ffcc00" stroke-width="4"/>
            <text x="300" y="240" fill="#ffcc00" font-size="14px" font-weight="bold" transform="rotate(23, 300, 240)">Carl's Jr. ★</text>

            <polygon points="385,268 415,254 415,285 385,299" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="400" y="250" fill="#fff" font-size="9px" font-weight="bold">V1</text>
            <polygon points="440,243 470,229 470,260 440,274" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="455" y="225" fill="#fff" font-size="9px" font-weight="bold">V2</text>
        """

        # COORDENADAS FIJAS PARA LAS POSICIONES DE LA FILA (Efecto de avance curvo)
        puntos_carril = [
            (545, 215),  # Q1: Siguiente listo para entrar a V2
            (590, 175),  # Q2
            (560, 135),  # Q3: Curva trasera superior
            (485, 110),  # Q4: Recta de atrás
            (410, 85),   # Q5
            (335, 60)    # Q6: Entrada al establecimiento
        ]

        # REPASO DE AUTOS ACTIVOS EN LAS VENTANILLAS (Color Rojo)
        if (st.session_state.v1.cliente_actual):
            svg_mapa += f"""
            <g transform="translate(410, 320)">
                <ellipse cx="0" cy="12" rx="26" ry="12" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-22,0 4,-12 24,-2 0,10" fill="#d32f2f"/>
                <polygon points="-10,-4 4,-11 16,-5 3,1" fill="#ef5350"/>
                <rect x="-35" y="-30" width="70" height="15" rx="3" fill="rgba(0,0,0,0.8)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v1.cliente_actual.nombre}</text>
                <text x="0" y="24" fill="#ffcc00" font-size="10px" font-weight="bold" text-anchor="middle" bgcolor="#000">{st.session_state.v1.estado}</text>
            </g>
            """
        else:
            svg_mapa += f'<text x="410" y="335" fill="#bbb" font-size="11px" font-style="italic" text-anchor="middle">V1: {st.session_state.v1.estado}</text>'

        if (st.session_state.v2.cliente_actual):
            svg_mapa += f"""
            <g transform="translate(470, 290)">
                <ellipse cx="0" cy="12" rx="26" ry="12" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-22,0 4,-12 24,-2 0,10" fill="#d32f2f"/>
                <polygon points="-10,-4 4,-11 16,-5 3,1" fill="#ef5350"/>
                <rect x="-35" y="-30" width="70" height="15" rx="3" fill="rgba(0,0,0,0.8)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v2.cliente_actual.nombre}</text>
                <text x="0" y="24" fill="#ffcc00" font-size="10px" font-weight="bold" text-anchor="middle">{st.session_state.v2.estado}</text>
            </g>
            """
        else:
            svg_mapa += f'<text x="480" y="305" fill="#bbb" font-size="11px" font-style="italic" text-anchor="middle">V2: {st.session_state.v2.estado}</text>'

        # REPASO DE AUTOS ESPERANDO EN LA FILA DE ACCESO (Color Azul)
        for index, auto in enumerate(st.session_state.cola_autos):
            if (index < len(puntos_carril)):
                cx, cy = puntos_carril[index]
                svg_mapa += f"""
                <g transform="translate({cx}, {cy})">
                    <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.35)"/>
                    <polygon points="-20,0 4,-11 22,-2 0,9" fill="#1976d2"/>
                    <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#42a5f5"/>
                    <rect x="-30" y="-28" width="60" height="14" rx="3" fill="rgba(30,30,30,0.85)"/>
                    <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                </g>
                """

        svg_mapa += "</svg>"
        contenedor_mapa_vivo.markdown(svg_mapa, unsafe_allow_html=True)

        # TABLA FINANCIERA LATERAL
        tickets_list = list(st.session_state.pila_tickets)
        with box_pila.container(border=True):
            if (tickets_list):
                for tk in reversed(tickets_list):
                    st.write(f"📌 **Ticket de {tk.nombre}** — Finalizado con ${tk.total:.2f}")
            else:
                st.caption("Esperando transacciones de ventanillas...")

        caja_total = sum(tk.total for tk in tickets_list)
        box_caja.metric(label="💰 Capital Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.2)

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡El turno ha concluido con total éxito! Todos los vehículos han cruzado el Drive-Thru.")
