# app.py
import streamlit as st
import streamlit.components.v1 as components
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
            time.sleep(1.5) # Tiempo para apreciar el coche en ventanilla
            
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
    if not st.session_state.simulacion_activa:
        if st.button("🚀 Iniciar Simulación 3D", type="primary", use_container_width=True):
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

    col_mapa, col_reporte = st.columns([5, 3])

    with col_mapa:
        contenedor_mapa_vivo = st.empty()

    with col_reporte:
        st.subheader("🧾 Historial de Caja (Pila - LIFO)")
        box_pila = st.empty()
        box_caja = st.empty()

    # --- RENDERIZADO DEL MAPA ISOMÉTRICO (PROCESAMIENTO SEGURO) ---
    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        
        # Estructura del mapa base en perspectiva isométrica
        svg_mapa = """
        <svg width="100%" height="480" viewBox="0 0 800 480" style="background-color:#4caf50; border-radius:15px; font-family: sans-serif; box-shadow: inset 0 0 40px rgba(0,0,0,0.2);">
            <path d="M 180,-20 L 460,110 L 720,110 L 740,240 L 520,340 L 220,470 L 100,410 L 440,260 L 140,120 Z" fill="#3a3a3a"/>
            <path d="M 280,30 L 465,115 Q 580,115 630,160 L 460,240 L 230,345" fill="none" stroke="#2c2c2c" stroke-width="70" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M 280,30 L 465,115 Q 580,115 630,160 L 460,240 L 230,345" fill="none" stroke="#ffcc00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="10,8"/>
            
            <g transform="translate(80, 70)">
                <rect x="-3" y="0" width="6" height="25" fill="#5d4037"/>
                <polygon points="0,-45 -22,-15 0,5 22,-15" fill="#2e7d32"/>
                <polygon points="0,-55 -15,-30 0,-10 15,-30" fill="#388e3c"/>
            </g>
            <g transform="translate(720, 380)">
                <rect x="-3" y="0" width="6" height="25" fill="#5d4037"/>
                <polygon points="0,-45 -22,-15 0,5 22,-15" fill="#2e7d32"/>
                <polygon points="0,-55 -15,-30 0,-10 15,-30" fill="#388e3c"/>
            </g>

            <g transform="translate(130, 260)">
                <line x1="0" y1="0" x2="0" y2="70" stroke="#222" stroke-width="5"/>
                <rect x="-35" y="-35" width="70" height="35" rx="5" fill="#d32f2f" stroke="#fff" stroke-width="2"/>
                <text x="0" y="-13" fill="#ffcc00" font-size="24px" font-weight="bold" text-anchor="middle">★</text>
                <text x="0" y="-4" fill="#ffffff" font-size="8px" font-weight="bold" text-anchor="middle">DRIVE THRU</text>
            </g>

            <polygon points="360,140 490,200 360,260 230,200" fill="#212121" stroke="#111" stroke-width="1"/>
            <polygon points="230,200 360,260 360,340 230,280" fill="#2e2e2e"/>
            <polygon points="360,260 490,200 490,280 360,340" fill="#424242"/>
            <polygon points="360,145 490,205 490,212 360,252" fill="none" stroke="#ffcc00" stroke-width="4"/>
            <polygon points="230,205 360,252 360,259 230,212" fill="none" stroke="#ffcc00" stroke-width="4"/>
            <text x="300" y="240" fill="#ffcc00" font-size="14px" font-weight="bold" transform="rotate(23, 300, 240)">Carl's Jr. ★</text>

            <polygon points="385,268 415,254 415,285 385,299" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="400" y="250" fill="#fff" font-size="10px" font-weight="bold">V1</text>
            <polygon points="440,243 470,229 470,260 440,274" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="455" y="225" fill="#fff" font-size="10px" font-weight="bold">V2</text>
        """

        # Coordenadas de la fila curva trasera
        puntos_carril = [
            (545, 215), (590, 175), (560, 135), (485, 110), (410, 85), (335, 60)
        ]

        # RENDERIZAR COCHES EN ATENCIÓN (Ventanilla 1)
        if st.session_state.v1.cliente_actual:
            svg_mapa += f"""
            <g transform="translate(410, 320)">
                <ellipse cx="0" cy="12" rx="26" ry="12" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-22,0 4,-12 24,-2 0,10" fill="#e53935"/>
                <polygon points="-10,-4 4,-11 16,-5 3,1" fill="#ef5350"/>
                <rect x="-40" y="-30" width="80" height="16" rx="4" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v1.cliente_actual.nombre}</text>
                <text x="0" y="26" fill="#ffcc00" font-size="11px" font-weight="bold" text-anchor="middle">{st.session_state.v1.estado}</text>
            </g>
            """
        else:
            svg_mapa += f'<text x="400" y="335" fill="#fff" font-size="11px" font-style="italic" text-anchor="middle">V1: {st.session_state.v1.estado}</text>'

        # RENDERIZAR COCHES EN ATENCIÓN (Ventanilla 2)
        if st.session_state.v2.cliente_actual:
            svg_mapa += f"""
            <g transform="translate(470, 290)">
                <ellipse cx="0" cy="12" rx="26" ry="12" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-22,0 4,-12 24,-2 0,10" fill="#e53935"/>
                <polygon points="-10,-4 4,-11 16,-5 3,1" fill="#ef5350"/>
                <rect x="-40" y="-30" width="80" height="16" rx="4" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.v2.cliente_actual.nombre}</text>
                <text x="0" y="26" fill="#ffcc00" font-size="11px" font-weight="bold" text-anchor="middle">{st.session_state.v2.estado}</text>
            </g>
            """
        else:
            svg_mapa += f'<text x="475" y="305" fill="#fff" font-size="11px" font-style="italic" text-anchor="middle">V2: {st.session_state.v2.estado}</text>'

        # RENDERIZAR VEHÍCULOS ESPERANDO EN LA COLA (Color Azul)
        for index, auto in enumerate(st.session_state.cola_autos):
            if index < len(puntos_carril):
                cx, cy = puntos_carril[index]
                svg_mapa += f"""
                <g transform="translate({cx}, {cy})">
                    <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.35)"/>
                    <polygon points="-20,0 4,-11 22,-2 0,9" fill="#1976d2"/>
                    <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#42a5f5"/>
                    <rect x="-35" y="-28" width="70" height="15" rx="3" fill="rgba(0,0,0,0.8)"/>
                    <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                </g>
                """

        svg_mapa += "</svg>"
        
        # Inyección web pura para evitar la rotura de Markdown
        components.html(svg_mapa, height=480)

        # SECCIÓN LATERAL: REPORTE FINANCIERO
        tickets_list = list(st.session_state.pila_tickets)
        with box_pila.container
