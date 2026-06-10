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
        self.estado = "⚓ Esperando cliente en el fondo del mar..."
        self.cliente_actual = None
        self.progreso = 0

    def run(self):
        while True:
            try:
                # Sacamos al cliente de la cola de forma segura
                cliente = self.cola_clientes.popleft()
            except IndexError:
                self.estado = "🔴 Turno Finalizado (Don Cangrejo cuenta los billetes)"
                break

            self.atender_cliente(cliente)

    def atender_cliente(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"📝 Tomando orden de {cliente.nombre}..."
        self.progreso = 10
        
        # Simulación de pedido aleatorio (Fórmula secreta)
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        # Simulación del tiempo de preparación con la eficiencia de Bob Esponja
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 ¡Bob Esponja está cocinando el pedido de {cliente.nombre}!"
        
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9) # Va subiendo hasta el 100%

        if (cliente.total > 0):
            self.estado = f"🍔 ¡Cangreburger Entregada a {cliente.nombre}!"
            self.pila_tickets.append(cliente)
            time.sleep(1.5) # Pausa para ver el éxito
            
        self.cliente_actual = None
        self.estado = "⚓ Esperando cliente en el fondo del mar..."
        self.progreso = 0


# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(page_title="Cangreburger - El Cangrejo Cascararrabias", page_icon="🍔", layout="wide")

# --- INYECCIÓN DE ESTILO CSS (Temática Submarina, Neón e IMAGEN DE FONDO) ---
# He añadido la URL de una imagen de fondo que recrea el mar de Fondo de Bikini.
# Puedes cambiar la URL por otra imagen si lo prefieres.
st.markdown("""
    <style>
    /* Imagen de fondo estilo mar de Bob Esponja */
    .stApp {
        background-image: url("https://img.freepik.com/foto-gratis/fondo-marino-caracteristico-dibujos-animados_23-2150165502.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: #f0f0f0; /* Texto claro para que contraste */
    }
    
    /* Overlay para oscurecer un poco el fondo y mejorar la legibilidad del texto */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.5); /* Semi-transparente negro */
        z-index: -1;
    }

    /* Títulos con estilo neón amarillo como el letrero principal */
    h1, h2, h3 {
        color: #ffcc00 !important;
        text-shadow: 0 0 10px rgba(255, 204, 0, 0.8);
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    
    /* Subtítulos en un azul eléctrico para que resalten */
    h4, h5, h6 {
        color: #00e6ff !important;
        text-shadow: 0 0 8px rgba(0, 230, 255, 0.6);
    }

    /* Estilo para los contenedores (Ventanillas) imitando metal de submarino/escotilla */
    div[data-testid="stBlock"] {
        background-color: rgba(13, 31, 45, 0.8) !important; /* Fondo semi-oscuro para contraste */
        border: 2px solid #4a6984 !important;
        border-radius: 15px;
        padding: 20px;
    }

    /* Customizar las métricas de dinero al estilo Don Cangrejo (Verde) */
    div[data-testid="stMetricValue"] {
        color: #4caf50 !important;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        color: #ffcc00 !important;
    }

    /* Estilo para el botón de inicio */
    button[kind="primary"] {
        background-color: #ffcc00 !important;
        color: #0d1f2d !important;
        border: 2px solid #ffcc00 !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    button[kind="primary"]:hover {
        background-color: #0d1f2d !important;
        color: #ffcc00 !important;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.7);
    }

    /* Estilo para los mensajes de info, success, warning */
    .stAlert {
        background-color: rgba(0, 0, 0, 0.3) !important;
        border-radius: 10px;
        color: #f0f0f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Encabezado principal basado en el póster
st.title("🍔 El Cangrejo Cascararrabias — Gestión de Pedidos")
st.markdown("### 🌊 ¡Resolviendo el CAOS en la cocina con Estructuras de Datos!")
st.write("Con la supervisión de **DON CANGREJO** y la eficiencia de **BOB ESPONJA**.")
st.write("---")

# 1. Definición del Menú Temático (Basado exactamente en la imagen)
if 'menu' not in st.session_state:
    st.session_state.menu = [
        Producto("🍔 Cangreburger Clásica", 85.00),
        Producto("🍟 Papas Fritas de Bob Esponja", 40.00),
        Producto("🥤 Batido Kelp de Don Cangrejo", 35.00),
        Producto("🍔 Cangreburger con Queso", 95.00)
    ]

# 2. Inicialización de los estados de la aplicación
if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

# --- BOTÓN DE DISPARO ---
if not st.session_state.simulacion_activa:
    if st.button("🚀 ¡Iniciar Proyecto de Turnos de Cangreburgers!", type="primary", use_container_width=True):
        # Clientes marinos o conocidos de Fondo de Bikini
        nombres = ["Patricio", "Calamardo", "Arenita", "Sra. Puff", "Plankton", "Gary", "Sirenmán", "Chico Percance"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        st.session_state.pila_tickets = []
        st.session_state.simulacion_activa = True
        st.rerun()

# --- MIENTRAS LA SIMULACIÓN ESTÉ CORRIENDO ---
if st.session_state.simulacion_activa:
    
    if 'v1' not in st.session_state or not st.session_state.v1.is_alive():
        st.session_state.v1 = CajeroVisual("👨‍🍳 Cocina de Bob Esponja", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("🦑 Mostrador de Calamardo", st.session_state.cola_autos, st.session_state.menu, st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()

    # Layout visual
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
        
        st.subheader("🦀 El Cofre de Don Cangrejo (Corte)")
        box_caja = st.empty()

    # CICLO DE REFRESCO DE LA PANTALLA
    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        
        # Ventanilla 1 Visual (Bob Esponja)
        with box_v1.container():
            st.markdown(f"#### {st.session_state.v1.nombre_cajero}")
            st.info(st.session_state.v1.estado)
            st.progress(st.session_state.v1.progreso)
            if st.session_state.v1.cliente_actual:
                st.caption(f"Cliente: **{st.session_state.v1.cliente_actual.nombre}**")

        # Ventan
