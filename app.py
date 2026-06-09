# app.py
import streamlit as st
import streamlit.components.v1 as components
import time
from collections import deque
import random
import threading
from producto import Producto
from cliente import Cliente

# --- HILO 1: BOCINA / INTERCOMUNICADOR DE ORDEN (ENTRADA) ---
class EstacionOrden(threading.Thread):
    def __init__(self, cola_clientes, cola_cocina, menu_restaurante, lock):
        super().__init__()
        self.cola_clientes = cola_clientes
        self.cola_cocina = cola_cocina
        self.menu = menu_restaurante
        self.lock = lock
        self.estado = "🎙️ Libre"
        self.cliente_actual = None

    def run(self):
        while True:
            with self.lock:
                if (len(self.cola_clientes) > 0):
                    cliente = self.cola_clientes.popleft()
                else:
                    self.estado = "🔴 Apagado"
                    break

            self.cliente_actual = cliente
            self.estado = "📝 Ordenando..."
            time.sleep(2.5) 
            
            cantidad_productos = random.randint(1, 3)
            for _ in range(cantidad_productos):
                producto_elegido = random.choice(self.menu)
                cliente.agregar_producto(producto_elegido)
            
            with self.lock:
                self.cola_cocina.append(cliente)
                
            self.cliente_actual = None
            self.estado = "🎙️ Libre"
        
        self.estado = "🔴 Apagado"

# --- HILO 2: VENTANILLA DE ENTREGA Y PAGO ---
class VentanillaEntrega(threading.Thread):
    def __init__(self, cola_cocina, pila_tickets, thread_orden, lock):
        super().__init__()
        self.cola_cocina = cola_cocina
        self.pila_tickets = pila_tickets
        self.thread_orden = thread_orden
        self.lock = lock
        self.estado = "☕ Esperando..."
        self.cliente_actual = None

    def run(self):
        while True:
            with self.lock:
                seguir_operando = (self.thread_orden.is_alive() or len(self.cola_cocina) > 0)
            
            if (not seguir_operando):
                break

            cliente = None
            with self.lock:
                if (len(self.cola_cocina) > 0):
                    cliente = self.cola_cocina.popleft()
            
            if (not cliente):
                self.estado = "☕ Esperando..."
                time.sleep(0.2)
                continue

            self.cliente_actual = cliente
            self.estado = "🍳 Preparando..."
            time.sleep(random.randint(4, 6))
            
            if (cliente.total > 0):
                self.estado = f"💰 Cobrando (${cliente.total:.0f})"
                with self.lock:
                    self.pila_tickets.append(cliente)
                time.sleep(2.5)
            
            self.cliente_actual = None
            
        self.estado = "🔴 Cerrado"

# --- CONFIGURACIÓN DE LA INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Lateral Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Vista Lateral Recta (Thread-Safe)")
st.write("Flujo lineal continuo en dos estaciones consecutivas en línea recta sin curvas.")
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
    st.session_state.posiciones_visuales = {}
    st.session_state.lock = threading.Lock()

col_btn, col_info = st.columns([1, 2])
with col_btn:
    if (not st.session_state.simulacion_activa):
        if (st.button("🚀 Iniciar Calle Recta", type="primary", use_container_width=True)):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.cola_cocina = deque()
            st.session_state.pila_tickets = []
            st.session_state.posiciones_visuales = {}
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if ('bocina' not in st.session_state or not st.session_state.bocina.is_alive()):
        st.session_state.bocina = EstacionOrden(st.session_state.cola_autos, st.session_state.cola_cocina, st.session_state.menu, st.session_state.lock)
        st.session_state.ventanilla = VentanillaEntrega(st.session_state.cola_cocina, st.session_state.pila_tickets, st.session_state.bocina, st.session_state.lock)
        st.session_state.bocina.start()
        st.session_state.ventanilla.start()

    col_mapa, col_reporte = st.columns([5, 3])
    with col_mapa:
        contenedor_mapa_vivo = st.empty()
    with col_reporte:
        st.subheader("🧾 Historial LIFO (Caja Registradora)")
        box_pila = st.empty()
        box_caja = st.empty()

    # --- PUNTOS ESTRATÉGICOS HORIZONTALES (VISTA LATERAL) ---
    # Eje Y fijo a 330px representando la altura de la calle recta
    Y_CALLE = 330
    X_BOCINA = 250
    X_VENTANILLA = 550

    while (st.session_state.ventanilla.is_alive() or st.session_state.bocina.is_alive() or len(st.session_state.posiciones_visuales) > 0):
        targets_actuales = {}

        with st.session_state.lock:
            copia_cola_autos = list(st.session_state.cola_autos)
            copia_cola_cocina = list(st.session_state.cola_cocina)
            copia_pila_tickets = list(st.session_state.pila_tickets)

        # 1. Autos esperando antes de la Bocina (Cola de entrada a la izquierda)
        for index, auto in enumerate(copia_cola_autos):
            tx = X_BOCINA - 90 - (index * 75)
            targets_actuales[auto.nombre] = (tx, Y_CALLE, "En espera", "#757575")

        # 2. Auto actualmente atendido en la Bocina
        if (st.session_state.bocina.cliente_actual):
            auto = st.session_state.bocina.cliente_actual
            targets_actuales[auto.nombre] = (X_BOCINA, Y_CALLE, st.session_state.bocina.estado, "#ff9100")

        # 3. Autos en el tramo intermedio entre la Bocina y la Ventanilla
        indice_offset = 1 if (st.session_state.ventanilla.cliente_actual) else 0
        for index, auto in enumerate(copia_cola_cocina):
            slot_actual = index + indice_offset
            if (slot_actual == 0):
                tx = X_VENTANILLA
            else:
                tx = X_VENTANILLA - (slot_actual * 75)
                
            # Si el auto todavía no pasa el espacio de la bocina físicamente, lo recorremos levemente
            if (tx <= X_BOCINA):
                tx = X_BOCINA + 60
            targets_actuales[auto.nombre] = (tx, Y_CALLE, "Avanzando...", "#0288d1")

        # 4. Auto actualmente atendido en la Ventanilla única
        if (st.session_state.ventanilla.cliente_actual):
            auto = st.session_state.ventanilla.cliente_actual
            targets_actuales[auto.nombre] = (X_VENTANILLA, Y_CALLE, st.session_state.ventanilla.estado, "#d32f2f")

        # 5. Autos saliendo del restaurante hacia la derecha de la pantalla
        nombres_activos = set(targets_actuales.keys())
        for nombre in list(st.session_state.posiciones_visuales.keys()):
            if (nombre not in nombres_activos):
                curr_x, _ = st.session_state.posiciones_visuales[nombre]
                if (curr_x > 840):
                    del st.session_state.posiciones_visuales[nombre]
                else:
                    targets_actuales[nombre] = (890, Y_CALLE, "¡Buen viaje! 🍔", "#2e7d32")

        # --- GENERACIÓN GRÁFICA DEL MAPA LATERAL SVG ---
        svg_autos = ""
        for nombre, (tx, ty, texto, color_hex) in targets_actuales.items():
            if (nombre not in st.session_state.posiciones_visuales):
                st.session_state.posiciones_visuales[nombre] = (-80, Y_CALLE)
            
            curr_x, curr_y = st.session_state.posiciones_visuales[nombre]
            new_x = curr_x + (tx - curr_x) * 0.15
            st.session_state.posiciones_visuales[nombre] = (new_x, ty)
            
            # Dibujo de un carro simplificado con perspectiva lateral estilizada
            svg_autos += f"""
            <g transform="translate({new_x:.1f}, {ty})">
                <ellipse cx="0" cy="18" rx="28" ry="6" fill="rgba(0,0,0,0.25)"/>
                <rect x="-26" y="-3" width="52" height="16" rx="4" fill="{color_hex}"/>
                <path d="M -16,-3 L -8,-14 L 10,-14 L 16,-3 Z" fill="#e0e0e0" stroke="{color_hex}" stroke-width="1"/>
                <polygon points="-6,-11 6,-11 11,-4 -6,-4" fill="#80deea"/>
                <circle cx="-15" cy="14" r="6" fill="#1a1a1a"/>
                <circle cx="-15" cy="14" r="2.5" fill="#eeeeee"/>
                <circle cx="15" cy="14" r="6" fill="#1a1a1a"/>
                <circle cx="15" cy="14" r="2.5" fill="#eeeeee"/>
                <rect x="-35" y="-34" width="70" height="14" rx="3" fill="rgba(0,0,0,0.8)"/>
                <text x="0" y="-24" fill="#ffffff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {nombre}</text>
            """
            if (texto):
                svg_autos += f'<text x="0" y="28" fill="#ffcc00" font-size="10px" font-weight="bold" text-anchor="middle">{texto}</text>'
            svg_autos += "</g>"

        svg_mapa_completo = f"""
        <svg width="100%" height="450" viewBox="0 0 800 450" style="background-color:#c8e6c9; border-radius:15px; font-family: sans-serif;">
            <rect x="0" y="0" width="800" height="260" fill="#bbdefb"/>
            <circle cx="730" cy="60" r="35" fill="#fff9c4"/>
            
            <rect x="200" y="110" width="450" height="150" fill="#3e2723" stroke="#212121" stroke-width="2"/>
            <rect x="200" y="95" width="450" height="15" fill="#ffcc00"/>
            <text x="425" y="145" fill="#ffcc00" font-size="28px" font-weight="bold" text-anchor="middle">★ Carl's Jr. ★</text>
            
            # --- ESTACIÓN 1: LA BOCINA ---
            <g transform="translate({X_BOCINA}, 260)">
                <line x1="0" y1="0" x2="0" y2="-60" stroke="#37474f" stroke-width="4"/>
                <rect x="-25" y="-85" width="50" height="25" rx="3" fill="#ffcc00" stroke="#111"/>
                <text x="0" y="-69" fill="#111" font-size="10px" font-weight="bold" text-anchor="middle">🎙️ MENU</text>
            </g>
            
            # --- ESTACIÓN 2: VENTANILLA ---
            <g transform="translate({X_VENTANILLA}, 260)">
                <rect x="-20" y="-55" width="40" height="45" fill="#80deea" stroke="#fff" stroke-width="2"/>
                <rect x="-25" y="-10" width="50" height="5" fill="#cfd8dc"/>
                <text x="0" y="-63" fill="#ffffff" font-size="11px" font-weight="bold" text-anchor="middle">🪟 VENTANILLA</text>
            </g>

            <rect x="0" y="260" width="800" height="120" fill="#424242"/>
            <line x1="0" y1="320" x2="800" y2="320" stroke="#ffcc00" stroke-width="2" stroke-dasharray="15,10"/>
            
            {svg_autos}
        </svg>
        """
        
        with contenedor_mapa_vivo:
            components.html(svg_mapa_completo, height=450, scrolling=False)

        with box_pila.container(border=True):
            if (copia_pila_tickets):
                for tk in reversed(copia_pila_tickets):
                    st.write(f"📌 **Pedido Entregado:** {tk.nombre} — Total cobrado: `${tk.total:.2f}`")
            else:
                st.caption("Ningún auto ha cruzado la ventanilla frontal aún...")

        caja_total = sum(tk.total for tk in copia_pila_tickets)
        box_caja.metric(label="💰 Capital Total Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.04)

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡Perfecto! La calle recta en perspectiva lateral funciona de forma fluida y sin interrupciones.")
