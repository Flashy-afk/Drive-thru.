import streamlit as st
import time
from collections import deque
import random
import threading
import base64

# --- FUNCIÓN PARA CARGAR LA IMAGEN LOCAL EN STREAMLIT ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(page_title="Cangreburger - El Cangrejo Cascararrabias", page_icon="🍔", layout="wide")

# Intentamos cargar tu imagen local 'fondo.jpg'
try:
    bin_str = get_base64_image("fondo.jpg")
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("<style>.stApp { background-color: #0d1f2d; }</style>", unsafe_allow_html=True)


# --- INYECCIÓN DEL ESTILO ADICIONAL (MÁXIMO CONTRASSTE Y VISIBILIDAD) ---
st.markdown("""
    <style>
    /* TÍTULOS PRINCIPALES (Fuera de las cajas): Azul industrial con borde blanco grueso */
    h1, h2, h3 {
        color: #001c3d !important;
        font-family: 'Arial Black', Gadget, sans-serif;
        -webkit-text-stroke: 1.5px #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
    }

    /* CONTENEDORES / CAJAS (Un poco más oscuras y sólidas para que no se transparente el dibujo de atrás) */
    div[data-testid="stMetric"], div[data-testid="stBlock"] {
        background-color: rgba(6, 20, 36, 0.95) !important; 
        border: 3px solid #4a6984 !important;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.6);
    }

    /* FORZAR QUE ABSOLUTAMENTE TODO EL TEXTO INTERNO SEA VISIBLE (Blanco y Amarillo) */
    div[data-testid="stBlock"] h4, 
    div[data-testid="stBlock"] p, 
    div[data-testid="stBlock"] span, 
    div[data-testid="stBlock"] div,
    div[data-testid="stBlock"] label,
    div[data-testid="stBlock"] small {
        color: #ffffff !important;
        -webkit-text-stroke: 0px !important;
        text-shadow: none !important;
        font-weight: bold !important;
    }

    /* Títulos secundarios dentro de las cajas (Ej. "Cocina de Bob Esponja") en Amarillo Neón */
    div[data-testid="stBlock"] h4 {
        color: #ffcc00 !important;
        font-size: 1.3rem !important;
    }

    /* ALERTAS DE STREAMLIT (Modificamos los cuadros de Info, Success y Warning para que se lean) */
    .stAlert {
        background-color: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    .stAlert div {
        color: #ffffff !important;
    }

    /* TEXTO DE LOS TICKETS (st.text) */
    .stText pre {
        color: #00ffcc !important; /* Estilo pantalla de computadora antigua */
        background-color: rgba(0, 0, 0, 0.4) !important;
        font-weight: bold !important;
    }

    /* MÉTRICAS DE DINERO (Don Cangrejo) */
    div[data-testid="stMetricValue"] {
        color: #4caf50 !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #ffcc00 !important;
        font-weight: bold !important;
    }

    /* BOTÓN ROJO DON CANGREJO */
    button[kind="primary"] {
        background-color: #d32f2f !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: 2px solid #ffffff !important;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
    }
    button[kind="primary"]:hover {
        background-color: #ffffff !important;
        color: #d32f2f !important;
        border: 2px solid #d32f2f !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- RECONFIGURACIÓN DEL CAJERO PARA EL FRONTEND ---
class CajeroVisual(threading.Thread):
    def __init__(self, nombre_cajero, cola_clientes, menu_restaurante, pila_tickets):
        super().__init__()
        self.nombre_cajero = nombre_cajero
        self.cola_clientes = cola_clientes
        self.menu = menu_restaurante
        self.pila_tickets = pila_tickets
        self.estado = "⚓ Esperando cliente en el fondo del mar..."
        self.cliente_actual = None
        self.progreso = 0

    def run(self):
        while True:
            try:
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Turno Finalizado (Don Cangrejo cuenta los billetes)"
                break

            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"📝 Tomando orden de {cliente.nombre}..."
        self.progreso = 10
        
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 ¡Bob Esponja está cocinando el pedido de {cliente.nombre}!"
        
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9)

        if (cliente.total > 0):
            self.estado = f"🍔 ¡Cangreburger Entregada a {cliente.nombre}!"
            self.pila_tickets.append(cliente)
            time.sleep(1.5)
            
        self.cliente_actual = None
        self.estado = "⚓ Esperando cliente en el fondo del mar..."
        self.progreso = 0


# --- CUERPO PRINCIPAL DEL FRONTEND ---
st.title("🍔 El Cangrejo Cascararrabias — Gestión de Pedidos")
st.markdown("### 🌊 ¡Resolviendo el CAOS en la cocina con Estructuras de Datos!")
st.write("Con la supervisión de **DON CANGREJO** y la eficiencia de **BOB ESPONJA**.")
st.write("---")

if 'menu' not in st.session_state:
    st.session_state.menu = [
        Producto("🍔 Cangreburger Clásica", 85.00),
        Producto("🍟 Papas Fritas de Bob Esponja", 40.00),
        Producto("🥤 Batido Kelp de Don Cangrejo", 35.00),
        Producto("🍔 Cangreburger con Queso", 95.00)
    ]

if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

if not st.session_state.simulacion_activa:
    if st.button("🚀 ¡Iniciar Proyecto de Turnos de Cangreburgers!", type="primary", use_container_width=True):
        nombres = ["Patricio", "Calamardo", "Arenita", "Sra. Puff", "Plankton", "Gary", "Sirenmán", "Chico Percance"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        st.session_state.pila_tickets = []
        st.session_state.simulacion_activa = True
        st.rerun()

if st.session_state.simulacion_activa:
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("👨‍🍳 Cocina de Bob Esponja", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("🦑 Mostrador de Calamardo", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    col_izquierda, col_derecha = st.columns([2, 1])

    with col_izquierda:
        st.subheader("⚙️ Ventanillas de Atención (Paralelo)")
        v_col1, v_col2 = st.columns(2)
        box_v1 = v_col1.empty()
        box_v2 = v_col2.empty()
        
        st.subheader("👥 Queue's (Colas de Clientes - FIFO)")
        box_cola = st.empty()

    with col_derecha:
        st.subheader("🗂️ Pilas (Stack de Tickets - LIFO)")
        box_pila = st.empty()
        
        st.subheader("🦀 El Cofre de Don Cangrejo")
        box_caja = st.empty()

    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        with box_v1.container(border=True):
            st.markdown(f"#### {st.session_state.v1.nombre_cajero}")
            st.info(st.session_state.v1.estado)
            st.progress(st.session_state.v1.progreso)
            if st.session_state.
