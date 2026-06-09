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
            self.estado = "📝 Ordenando..."
            time.sleep(2.5) # Interacción con el menú
            
            cantidad_productos = random.randint(1, 3)
            for _ in range(cantidad_productos):
                producto_elegido = random.choice(self.menu)
                cliente.agregar_producto(producto_elegido)
            
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
        self.estado = "☕ Esperando..."
        self.cliente_actual = None

    def run(self):
        while (self.thread_orden.is_alive() or len(self.cola_cocina) > 0):
            try:
                cliente = self.cola_cocina.popleft()
            except IndexError:
                self.estado = "☕ Esperando..."
                time.sleep(0.1)
                continue

            self.cliente_actual = cliente
            
            # Tiempo en cocina
            tiempo_preparacion = random.randint(4, 7)
            self.estado = "🍳 Cocinando..."
            time.sleep(tiempo_preparacion)
            
            # Entrega y Cobro
            if (cliente.total > 0):
                self.estado = f"💰 Cobrando (${cliente.total:.0f})"
                self.pila_tickets.append(cliente)
                time.sleep(3.0) # Tiempo de atención final en ventanilla
            
            self.cliente_actual = None
            
        self.estado = "🔴 Cerrado"

# --- CONFIGURACIÓN DE LA INTERFAZ STREAMLIT ---
st.set_page_config(page_title="Carl's Jr. Smooth Drive-Thru", page_icon="🍔", layout="wide")

st.title("🍔 Carl's Jr. — Simulación Drive-Thru con Movimiento Fluido")
st.write("Motor de interpolación de coordenadas a alta tasa de frames para transiciones cinemáticas continuas.")
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
    st.session_state.posiciones_visuales = {} # Diccionario persistente de posiciones fluidas

col_btn, col_info = st.columns([1, 2])
with col_btn:
    if (not st.session_state.simulacion_activa):
        if (st.button("🚀 Iniciar Circuito de Alta Fluidez", type="primary", use_container_width=True)):
            nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
            st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
            st.session_state.cola_cocina = deque()
            st.session_state.pila_tickets = []
            st.session_state.posiciones_visuales = {} # Resetear posiciones de autos
            st.session_state.simulacion_activa = True
            st.rerun()

if (st.session_state.simulacion_activa):
    if ('bocina' not in st.session_state or not st.session_state.bocina.is_alive()):
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

    # Coordenadas clave de las estaciones
    puntos_entrada = [(240, 150), (195, 175), (150, 200), (105, 225)]
    puntos_giro_espera = [
        (470, 310),  # Slot 0: Ventanilla de Entrega
        (550, 255),  # Slot 1: Curva lateral de espera
        (585, 200),  # Slot 2: Lateral derecho
        (565, 145),  # Slot 3: Curva trasera superior derecha
        (510, 110),  # Slot 4: Recta trasera central
        (430, 95),   # Slot 5: Recta trasera izquierda
        (350, 100)   # Slot 6: Inmediatamente después de ordenar
    ]

    # --- CICLO DE ANIMACIÓN DE ALTO RENDIMIENTO (25 FPS) ---
    # El ciclo continúa activo mientras haya hilos corriendo o queden autos visuales saliendo del mapa
    while (st.session_state.ventanilla.is_alive() or st.session_state.bocina.is_alive() or len(st.session_state.posiciones_visuales) > 0):
        
        # Mapeo temporal de objetivos: { nombre: (target_x, target_y, texto, color) }
        targets_actuales = {}

        # 1. Posicionar autos en la fila de entrada (Antes de la bocina)
        for index, auto in enumerate(st.session_state.cola_autos):
            if (index < len(puntos_entrada)):
                tx, ty = puntos_entrada[index]
            else:
                tx, ty = (105 - (index - 3) * 40, 225)
            targets_actuales[auto.nombre] = (tx, ty, "", "#757575")

        # 2. Posicionar auto en la bocina de orden
        if (st.session_state.bocina.cliente_actual):
            auto = st.session_state.bocina.cliente_actual
            targets_actuales[auto.nombre] = (285, 125, st.session_state.bocina.estado, "#ff9100")

        # 3. Posicionar autos avanzando/esperando en el carril circular
        lista_transito = list(st.session_state.cola_cocina)
        indice_offset = 1 if (st.session_state.ventanilla.cliente_actual) else 0
        for index, auto in enumerate(lista_transito):
            slot_actual = index + indice_offset
            if (slot_actual < len(puntos_giro_espera)):
                tx, ty = puntos_giro_espera[slot_actual]
                targets_actuales[auto.nombre] = (tx, ty, "Preparando...", "#0288d1")

        # 4. Posicionar auto en la ventanilla de entrega frontal
        if (st.session_state.ventanilla.cliente_actual):
            auto = st.session_state.ventanilla.cliente_actual
            tx, ty = puntos_giro_espera[0]
            targets_actuales[auto.nombre] = (tx, ty, st.session_state.ventanilla.estado, "#d32f2f")

        # 5. Lógica de escape: Autos que ya salieron de las estructuras pero siguen en el mapa
        nombres_activos = set(targets_actuales.keys())
        for nombre in list(st.session_state.posiciones_visuales.keys()):
            if (nombre not in nombres_activos):
                curr_x, curr_y = st.session_state.posiciones_visuales[nombre]
                # Si el auto ya cruzó la meta de salida, lo eliminamos de memoria por completo
                if (curr_x < 190 and curr_y > 440):
                    del st.session_state.posiciones_visuales[nombre]
                else:
                    # Enrutamiento hacia la salida de la carretera (Borde inferior izquierdo)
                    targets_actuales[nombre] = (160, 450, "¡Buen provecho! 🍔", "#2e7d32")

        # --- CONSTRUCCIÓN DEL LIENZO SVG CON LERP ---
        svg_autos = ""
        for nombre, (tx, ty, texto, color_hex) in targets_actuales.items():
            # Si el auto aparece por primera vez, nace fuera del mapa por la izquierda
            if (nombre not in st.session_state.posiciones_visuales):
                st.session_state.posiciones_visuales[nombre] = (-40, 250)
            
            curr_x, curr_y = st.session_state.posiciones_visuales[nombre]
            
            # ECUACIÓN LERP: Posición = Actual + (Destino - Actual) * Factor_Velocidad
            # Un factor de 0.18 calculando a 25fps genera una transición de frenado suave estética
            new_x = curr_x + (tx - curr_x) * 0.18
            new_y = curr_y + (ty - curr_y) * 0.18
            st.session_state.posiciones_visuales[nombre] = (new_x, new_y)
            
            color_techo = "#bdbdbd" if color_hex == "#757575" else "#ffb74d" if color_hex == "#ff
