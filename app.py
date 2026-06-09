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
    def __init__(self, cola_clientes, cola_cocina, menu_restaurante):
        super().__init__()
        self.cola_clientes = cola_clientes
        self.cola_cocina = cola_cocina
        self.menu = menu_restaurante
        self.estado = "🎙️ Libre"
        self.cliente_actual = None

    def run(self):
        while True:
            try:
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Apagado"
                break

            self.cliente_actual = cliente
            self.estado = "📝 Tomando Orden..."
            time.sleep(2.5) # Tiempo de interacción con la bocina
            
            # Selección de productos aleatorios
            cantidad_productos = random.randint(1, 3)
            for _ in range(cantidad_productos):
                producto_elegido = random.choice(self.menu)
                cliente.agregar_producto(producto_elegido)
            
            # Al terminar de ordenar, el auto avanza al carril de circulación/cocina
            self.cola_cocina.append(cliente)
            self.cliente_actual = None
            self.estado = "🎙️ Libre"
        
        self.estado = "🔴 Apagado"

# --- HILO 2: VENTANILLA DE ENTREGA Y PAGO (FACHADA PRINCIPAL) ---
class VentanillaEntrega(threading.Thread):
    def __init__(self, cola_cocina, pila_tickets, thread_orden):
        super().__init__()
        self.cola_cocina = cola_cocina
        self.pila_tickets = pila_tickets
        self.thread_orden = thread_orden
        self.estado = "☕ Esperando auto..."
        self.cliente_actual = None
        self.progreso = 0

    def run(self):
        # Sigue operando si la bocina sigue activa o si quedan autos en el carril de tránsito hacia la ventana
        while (self.thread_orden.is_alive() or len(self.cola_cocina) > 0):
            try:
                cliente = self.cola_cocina.popleft()
            except IndexError:
                self.estado = "☕ Esperando auto..."
                time.sleep(0.2)
                continue

            self.cliente_actual = cliente
            
            # 1. Simulación del tiempo de preparación en cocina
            tiempo_preparacion = random.randint(4, 7)
            self.estado = "🍳 Cocinando pedido..."
            for i in range(10):
                time.sleep(tiempo_preparacion / 10)
                self.progreso = (i + 1) * 10
            
            # 2. Cobro en caja y entrega final
            if (cliente.total > 0):
                self.estado = f"💰 Entregando (${cliente.total:.0f})"
                self.pila_tickets.append(cliente)
                time.sleep(3.0) # Margen de tiempo para ver la salida del auto
            
            self.cliente_actual = None
            self.progreso = 0
            
        self.estado = "🔴 Cerrado"

# --- CONFIGURACIÓN DE LA INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Circular Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Simulación Inmersiva de Drive-Thru Circular")
st.write("Los clientes ordenan en la **Bocina de Menú**, giran alrededor del edificio en fila y recogen en la **Ventanilla de Entrega**.")
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
        if (st.button("🚀 Arrancar Circuito Drive-Thru", type="primary", use_container_width=True)):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.cola_cocina = deque()
            st.session_state.pila_tickets = []
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if ('bocina' not in st.session_state or not st.session_state.bocina.is_alive()):
        # Instanciar hilos con la nueva distribución lógica
        st.session_state.bocina = EstacionOrden(st.session_state.cola_autos, st.session_state.cola_cocina, st.session_state.menu)
        st.session_state.ventanilla = VentanillaEntrega(st.session_state.cola_cocina, st.session_state.pila_tickets, st.session_state.bocina)
        st.session_state.bocina.start()
        st.session_state.ventanilla.start()

    col_mapa, col_reporte = st.columns([5, 3])

    with col_mapa:
        contenedor_mapa_vivo = st.empty()

    with col_reporte:
        st.subheader("🧾 Historial LIFO (Caja Registradora)")
        box_pila = st.empty()
        box_caja = st.empty()

    # --- CICLO DE ANIMACIÓN Y CONTROL DE COORDENADAS ---
    while (st.session_state.ventanilla.is_alive() or st.session_state.bocina.is_alive()):
        
        svg_mapa = """
        <svg width="100%" height="480" viewBox="0 0 800 480" style="background-color:#2e7d32; border-radius:15px; font-family: sans-serif; box-shadow: inset 0 0 40px rgba(0,0,0,0.4);">
            <path d="M 80,240 L 250,140 Q 420,50 580,120 L 610,180 L 580,240 L 460,330 L 280,410" fill="none" stroke="#262626" stroke-width="75" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M 80,240 L 250,140 Q 420,50 580,120 L 610,180 L 580,240 L 460,330 L 280,410" fill="none" stroke="#ffcc00" stroke-width="2" stroke-dasharray="8,6" stroke-linecap="round" stroke-linejoin="round"/>
            
            <g transform="translate(60, 80)"><rect x="-3" y="0" width="6" height="20" fill="#5d4037"/><polygon points="0,-35 -18,-10 18,-10" fill="#1b5e20"/></g>
            <g transform="translate(730, 360)"><rect x="-3" y="0" width="6" height="20" fill="#5d4037"/><polygon points="0,-35 -18,-10 18,-10" fill="#1b5e20"/></g>

            <g transform="translate(260, 80)">
                <line x1="0" y1="0" x2="0" y2="35" stroke="#424242" stroke-width="4"/>
                <rect x="-25" y="-25" width="50" height="25" rx="4" fill="#ffcc00" stroke="#111" stroke-width="1.5"/>
                <text x="0" y="-9" fill="#111" font-size="10px" font-weight="bold" text-anchor="middle">📢 MENU</text>
            </g>

            <polygon points="290,230 400,290 400,220 290,160" fill="#212121" stroke="#111" stroke-width="0.5"/> <polygon points="400,290 510,220 510,150 400,220" fill="#3e2723" stroke="#111" stroke-width="0.5"/> <polygon points="400,220 510,150 400,90 290,160" fill="#151515"/> <polygon points="400,220 510,150 400,90 290,160" fill="none" stroke="#ffcc00" stroke-width="3" stroke-linejoin="round"/>
            <text x="320" y="210" fill="#ffcc00" font-size="14px" font-weight="bold" transform="rotate(25, 320, 210)">★ Carl's Jr.</text>

            <polygon points="420,250 445,234 445,265 420,281" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="430" y="215" fill="#ffffff" font-size="11px" font-weight="bold">Ventanilla Entrega</text>
        """

        # Coordenadas estáticas de la fila inicial antes de llegar a la bocina
        puntos_entrada = [
            (240, 150), (195, 175), (150, 200), (105, 225)
        ]

        # Coordenadas ordenadas de atrás hacia adelante rodeando el edificio (Para autos que ya ordenaron)
        puntos_giro_espera = [
            (470, 310),  # Slot 0: Justo en la Ventanilla de Entrega
            (550, 255),  # Slot 1: Saliendo de la curva lateral derecha
            (585, 200),  # Slot 2: Bajando por el lateral derecho
            (565, 145),  # Slot 3: Entrando a la curva superior derecha
            (510, 110),  # Slot 4: En la parte de atrás del edificio
            (430, 95),   # Slot 5: Avanzando por la recta trasera
            (350, 100)   # Slot 6: Inmediatamente después de la bocina
        ]

        # 1. AUTO ACTUAL EN LA BOCINA DE ORDEN
        if (st.session_state.bocina.cliente_actual):
            svg_mapa += f"""
            <g transform="translate(285, 125)">
                <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-20,0 4,-11 22,-2 0,9" fill="#ff9100"/>
                <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#ffb74d"/>
                <rect x="-45" y="-30" width="90" height="16" rx="4" fill="rgba(0,0,0,0.9)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.bocina.cliente_actual.nombre}</text>
                <text x="0" y="25" fill="#ffcc00" font-size="10px" font-weight="bold" text-anchor="middle">{st.session_state.bocina.estado}</text>
            </g>
            """

        # 2. AUTOS MOVIÉNDOSE / GIRANDO ALREDEDOR DEL EDIFICIO (Cola Cocina)
        # Convertimos la cola a lista para indexar sus posiciones en el carril
        lista_transito = list(st.session_state.cola_cocina)
        
        # Desplazamiento dinámico basado en si la ventanilla está ocupada
        indice_offset = 0
        if (st.session_state.ventanilla.cliente_actual):
            indice_offset = 1 # Si la ventana está ocupada, los de atrás se detienen un paso antes

        for index, auto in enumerate(lista_transito):
            slot_actual = index + indice_offset
            if (slot_actual < len(puntos_giro_espera)):
                cx, cy = puntos_giro_espera[slot_actual]
                svg_mapa += f"""
                <g transform="translate({cx}, {cy})">
                    <ellipse cx="0" cy="12" rx="22" ry="10" fill="rgba(0,0,0,0.3)"/>
                    <polygon points="-18,0 4,-10 20,-2 0,8" fill="#0288d1"/>
                    <polygon points="-8,-4 4,-9 14,-5 2,1" fill="#29b6f6"/>
                    <rect x="-40" y="-28" width="80" height="15" rx="3" fill="rgba(0,0,0,0.85)"/>
                    <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                    <text x="0" y="23" fill="#81d4fa" font-size="8px" text-anchor="middle">En tránsito V1</text>
                </g>
                """

        # 3. AUTO ACTUAL EN LA VENTANILLA DE ENTREGA (FRONTAL)
        if (st.session_state.ventanilla.cliente_actual):
            cx_v1, cy_v1 = puntos_giro_espera[0]
            svg_mapa += f"""
            <g transform="translate({cx_v1}, {cy_v1})">
                <ellipse cx="0" cy="12" rx="24" ry="11" fill="rgba(0,0,0,0.4)"/>
                <polygon points="-20,0 4,-11 22,-2 0,9" fill="#d32f2f"/>
                <polygon points="-9,-4 4,-10 15,-5 2,1" fill="#ef5350"/>
                <rect x="-45" y="-30" width="90" height="16" rx="4" fill="rgba(0,0,0,0.9)"/>
                <text x="0" y="-19" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {st.session_state.ventanilla.cliente_actual.nombre}</text>
                <text x="0" y="25" fill="#ffeb3b" font-size="10px" font-weight="bold" text-anchor="middle">{st.session_state.ventanilla.estado}</text>
            </g>
            """

        # 4. FILA DE ESPERA DE ACCESO (Antes de pasar a la Bocina de Orden)
        for index, auto in enumerate(st.session_state.cola_autos):
            if (index < len(puntos_entrada)):
                cx, cy = puntos_entrada[index]
                svg_mapa += f"""
                <g transform="translate({cx}, {cy})">
                    <ellipse cx="0" cy="12" rx="22" ry="10" fill="rgba(0,0,0,0.3)"/>
                    <polygon points="-18,0 4,-10 20,-2 0,8" fill="#757575"/>
                    <polygon points="-8,-4 4,-9 14,-5 2,1" fill="#bdbdbdb"/>
                    <rect x="-35" y="-28" width="70" height="15" rx="3" fill="rgba(0,0,0,0.8)"/>
                    <text x="0" y="-18" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {auto.nombre}</text>
                </g>
                """

        svg_mapa += "</svg>"
        
        with contenedor_mapa_vivo:
            components.html(svg_mapa, height=480)

        # DESPLIEGUE DEL REPORTE HISTÓRICO DE VENTAS
        tickets_list = list(st.session_state.pila_tickets)
        with box_pila.container(border=True):
            if (tickets_list):
                for tk in reversed(tickets_list):
                    st.write(f"📌 **Pedido Entregado:** {tk.nombre} — Total cobrado: `${tk.total:.2f}`")
            else:
                st.caption("Ningún auto ha cruzado la ventanilla frontal aún...")

        caja_total = sum(tk.total for tk in tickets_list)
        box_caja.metric(label="💰 Capital Total Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.25) # Control de refresco suave de la simulación

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡Excelente flujo! Todos los vehículos ordenaron en el intercomunicador, rodearon el edificio con éxito y retiraron sus pedidos en ventanilla.")
