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
            # Bloqueo seguro para extraer de la cola compartida
            with self.lock:
                if (len(self.cola_clientes) > 0):
                    cliente = self.cola_clientes.popleft()
                else:
                    self.estado = "🔴 Apagado"
                    break

            self.cliente_actual = cliente
            self.estado = "📝 Ordenando..."
            time.sleep(2.5) # Interacción con el menú fuera del lock para no congelar la app
            
            cantidad_productos = random.randint(1, 3)
            for _ in range(cantidad_productos):
                producto_elegido = random.choice(self.menu)
                cliente.agregar_producto(producto_elegido)
            
            # Bloqueo seguro para insertar en la siguiente cola
            with self.lock:
                self.cola_cocina.append(cliente)
                
            self.cliente_actual = None
            self.estado = "🎙️ Libre"
        
        self.estado = "🔴 Apagado"

# --- HILO 2: VENTANILLA DE ENTREGA Y PAGO (FACHADA PRINCIPAL) ---
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
            # Verificar de forma segura si debemos seguir operando
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
                time.sleep(0.1)
                continue

            self.cliente_actual = cliente
            self.estado = "🍳 Cocinando..."
            time.sleep(random.randint(4, 7))
            
            if (cliente.total > 0):
                self.estado = f"💰 Cobrando (${cliente.total:.0f})"
                with self.lock:
                    self.pila_tickets.append(cliente)
                time.sleep(3.0) # Tiempo de atención final
            
            self.cliente_actual = None
            
        self.estado = "🔴 Cerrado"

# --- CONFIGURACIÓN DE LA INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Thread-Safe Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Simulación Drive-Thru Concurrente Seguro")
st.write("Animación fluida a 25 FPS sincronizada mediante un cerrojo mutuo (`threading.Lock`) para prevenir colisiones.")
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
    st.session_state.lock = threading.Lock() # Inicialización del Lock global

col_btn, col_info = st.columns([1, 2])
with col_btn:
    if (not st.session_state.simulacion_activa):
        if (st.button("🚀 Iniciar Circuito de Alta Fluidez", type="primary", use_container_width=True)):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.cola_cocina = deque()
            st.session_state.pila_tickets = []
            st.session_state.posiciones_visuales = {}
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if ('bocina' not in st.session_state or not st.session_state.bocina.is_alive()):
        # Se pasa el Lock como argumento a ambos hilos concurrentes
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

    puntos_entrada = [(240, 150), (195, 175), (150, 200), (105, 225)]
    puntos_giro_espera = [
        (470, 310), (550, 255), (585, 200), (565, 145), (510, 110), (430, 95), (350, 100)
    ]

    # --- CICLO DE ANIMACIÓN SEGURO (25 FPS) ---
    while (st.session_state.ventanilla.is_alive() or st.session_state.bocina.is_alive() or len(st.session_state.posiciones_visuales) > 0):
        
        targets_actuales = {}

        # FASE CRÍTICA: Tomamos una instantánea rápida de las estructuras bajo el Lock
        with st.session_state.lock:
            copia_cola_autos = list(st.session_state.cola_autos)
            copia_cola_cocina = list(st.session_state.cola_cocina)
            copia_pila_tickets = list(st.session_state.pila_tickets)

        # 1. Procesar posiciones de entrada de la copia segura
        for index, auto in enumerate(copia_cola_autos):
            if (index < len(puntos_entrada)):
                tx, ty = puntos_entrada[index]
            else:
                tx, ty = (105 - (index - 3) * 40, 225)
            targets_actuales[auto.nombre] = (tx, ty, "", "#757575")

        # 2. Posicionar auto en la bocina de orden
        if (st.session_state.bocina.cliente_actual):
            auto = st.session_state.bocina.cliente_actual
            targets_actuales[auto.nombre] = (285, 125, st.session_state.bocina.estado, "#ff9100")

        # 3. Procesar carril circular de la copia segura
        indice_offset = 1 if (st.session_state.ventanilla.cliente_actual) else 0
        for index, auto in enumerate(copia_cola_cocina):
            slot_actual = index + indice_offset
            if (slot_actual < len(puntos_giro_espera)):
                tx, ty = puntos_giro_espera[slot_actual]
                targets_actuales[auto.nombre] = (tx, ty, "Preparando...", "#0288d1")

        # 4. Posicionar auto en la ventanilla frontal
        if (st.session_state.ventanilla.cliente_actual):
            auto = st.session_state.ventanilla.cliente_actual
            tx, ty = puntos_giro_espera[0]
            targets_actuales[auto.nombre] = (tx, ty, st.session_state.ventanilla.estado, "#d32f2f")

        # 5. Lógica cinemática de escape
        nombres_activos = set(targets_actuales.keys())
        for nombre in list(st.session_state.posiciones_visuales.keys()):
            if (nombre not in nombres_activos):
                curr_x, curr_y = st.session_state.posiciones_visuales[nombre]
                if (curr_x < 190 and curr_y > 440):
                    del st.session_state.posiciones_visuales[nombre]
                else:
                    targets_actuales[nombre] = (160, 450, "¡Buen provecho! 🍔", "#2e7d32")

        # --- RENDERIZACIÓN GRÁFICA SVG ---
        svg_autos = ""
        for nombre, (tx, ty, texto, color_hex) in targets_actuales.items():
            if (nombre not in st.session_state.posiciones_visuales):
                st.session_state.posiciones_visuales[nombre] = (-40, 250)
            
            curr_x, curr_y = st.session_state.posiciones_visuales[nombre]
            new_x = curr_x + (tx - curr_x) * 0.18
            new_y = curr_y + (ty - curr_y) * 0.18
            st.session_state.posiciones_visuales[nombre] = (new_x, new_y)
            
            color_techo = "#bdbdbd" if color_hex == "#757575" else "#ffb74d" if color_hex == "#ff9100" else "#29b6f6" if color_hex == "#0288d1" else "#ef5350"
            
            svg_autos += f"""
            <g transform="translate({new_x:.1f}, {new_y:.1f})">
                <ellipse cx="0" cy="12" rx="22" ry="10" fill="rgba(0,0,0,0.3)"/>
                <polygon points="-18,0 4,-10 20,-2 0,8" fill="{color_hex}"/>
                <polygon points="-8,-4 4,-9 14,-5 2,1" fill="{color_techo}"/>
                <rect x="-42" y="-28" width="84" height="15" rx="3" fill="rgba(0,0,0,0.85)"/>
                <text x="0" y="-17" fill="#fff" font-size="9px" font-weight="bold" text-anchor="middle">🚗 {nombre}</text>
            """
            if (texto):
                svg_autos += f'<text x="0" y="24" fill="#ffcc00" font-size="9px" font-weight="bold" text-anchor="middle">{texto}</text>'
            svg_autos += "</g>"

        svg_mapa_completo = f"""
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

            <polygon points="290,230 400,290 400,220 290,160" fill="#212121" stroke="#111" stroke-width="0.5"/>
            <polygon points="400,290 510,220 510,150 400,220" fill="#3e2723" stroke="#111" stroke-width="0.5"/>
            <polygon points="400,220 510,150 400,90 290,160" fill="#151515"/>
            <polygon points="400,220 510,150 400,90 290,160" fill="none" stroke="#ffcc00" stroke-width="3" stroke-linejoin="round"/>
            <text x="320" y="210" fill="#ffcc00" font-size="14px" font-weight="bold" transform="rotate(25, 320, 210)">★ Carl's Jr.</text>

            <polygon points="420,250 445,234 445,265 420,281" fill="#80deea" stroke="#fff" stroke-width="1"/>
            <text x="430" y="215" fill="#ffffff" font-size="11px" font-weight="bold">Ventanilla Entrega</text>
            
            {svg_autos}
        </svg>
        """
        
        with contenedor_mapa_vivo:
            components.html(svg_mapa_completo, height=480)

        # DESPLIEGUE DEL REPORTE MEDIANTE LA COPIA SEGURA
        with box_pila.container(border=True):
            if (copia_pila_tickets):
                for tk in reversed(copia_pila_tickets):
                    st.write(f"📌 **Pedido Entregado:** {tk.nombre} — Total cobrado: `${tk.total:.2f}`")
            else:
                st.caption("Ningún auto ha cruzado la ventanilla frontal aún...")

        caja_total = sum(tk.total for tk in copia_pila_tickets)
        box_caja.metric(label="💰 Capital Total Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.04) # Sincronización estable de fotogramas

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡Excelente! Ejecutándose de forma súper fluida a 25 FPS sin interrupciones concurrentes.")
