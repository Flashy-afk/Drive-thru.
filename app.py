import streamlit as st
import time
from collections import deque
import random
import base64

# =========================================================================
# 1. IMPORTACIÓN DE TUS MÓDULOS DE GITHUB
# =========================================================================
from producto import Producto
from cliente import Cliente
from cajero import Cajero  # Importamos tu clase original

# =========================================================================
# 2. ADAPTACIÓN DEL CAJERO PARA LA WEB (HERENCIA)
# =========================================================================
class CajeroVisual(Cajero):
    def __init__(self, nombre_cajero, cola_clientes, menu_restaurante, pila_tickets):
        # Llamamos al constructor de tu clase padre (cajero.py)
        super().__init__(nombre_cajero, cola_clientes, menu_restaurante, pila_tickets)
        
        # Añadimos variables exclusivas para la interfaz gráfica
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
            self.atender_cliente_visual(cliente)

    def atender_cliente_visual(self, cliente):
        self.cliente_actual = cliente
        self.estado = f"📝 Tomando orden de {cliente.nombre}..."
        self.progreso = 10
        
        # Replicamos la lógica de tu cajero.py, pero animando la pantalla
        cantidad_productos = random.randint(1, 3)
        for _ in range(cantidad_productos):
            producto_elegido = random.choice(self.menu)
            cliente.agregar_producto(producto_elegido)
            
        tiempo_preparacion = random.randint(2, 5)
        self.estado = f"🍳 ¡Bob Esponja está cocinando el pedido de {cliente.nombre}!"
        
        for i in range(10):
            time.sleep(tiempo_preparacion / 10)
            self.progreso = 10 + (i * 9)

        if cliente.total > 0:
            self.estado = f"🍔 ¡Cangreburger Entregada a {cliente.nombre}!"
            self.pila_tickets.append(cliente)
            time.sleep(1.5)
            
        self.cliente_actual = None
        self.estado = "⚓ Esperando cliente en el fondo del mar..."
        self.progreso = 0


# =========================================================================
# 3. CARGA DE ASSETS Y CONFIGURACIÓN
# =========================================================================
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

st.set_page_config(page_title="Cangreburger - El Cangrejo Cascararrabias", page_icon="🍔", layout="wide")

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
    st.markdown("<style>.stApp { background-color: #34495e; }</style>", unsafe_allow_html=True)


# =========================================================================
# 4. ESTILOS VISUALES (PANEL OSCURO Y TEXTOS NÍTIDOS)
# =========================================================================
st.markdown("""
    <style>
    /* PANEL PRINCIPAL: Cristal polarizado oscuro detrás de la app */
    .block-container {
        background-color: rgba(15, 25, 35, 0.85) !important; /* Fondo muy oscuro */
        padding: 3rem !important;
        border-radius: 20px !important;
        margin-top: 2rem !important;
        margin-bottom: 2rem !important;
        box-shadow: 0 0 20px rgba(0,0,0,0.8);
    }

    /* TÍTULOS PRINCIPALES: Amarillo brillante con borde negro */
    h1, h2, h3 {
        color: #ffcc00 !important;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 3px 3px 5px #000000, -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000 !important;
    }

    /* SUBTÍTULOS Y ETIQUETAS: Forzados a blanco puro con sombra */
    h4, p, span, div, label {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px #000000 !important;
        font-weight: bold !important;
    }

    /* CAJAS DE ESTADO (Alertas y success) */
    .stAlert {
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 2px solid #00ffcc !important;
        border-radius: 10px;
    }

    /* TEXTO DE LA PILA DE TICKETS */
    .stText pre {
        color: #00ffcc !important;
        background-color: rgba(0, 0, 0, 0.8) !important;
        font-size: 16px !important;
        border-left: 5px solid #ffcc00 !important;
        padding: 10px !important;
        text-shadow: none !important;
    }

    /* COFRE DE DON CANGREJO (Métricas) */
    div[data-testid="stMetricValue"] {
        color: #2ecc71 !important;
        font-size: 3rem !important;
        text-shadow: 2px 2px 5px #000000 !important;
    }

    /* BOTÓN DE INICIO */
    button[kind="primary"] {
        background-color: #c0392b !important;
        color: #ffffff !important;
        font-size: 20px !important;
        border: 3px solid #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================================
# 5. INTERFAZ DE USUARIO PRINCIPAL
# =========================================================================
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
        nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
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
            if st.session_state.v1.cliente_actual:
                st.markdown(f"Cliente: **{st.session_state.v1.cliente_actual.nombre}**")

        with box_v2.container(border=True):
            st.markdown(f"#### {st.session_state.v2.nombre_cajero}")
            st.info(st.session_state.v2.estado)
            st.progress(st.session_state.v2.progreso)
            if st.session_state.v2.cliente_actual:
                st.markdown(f"Cliente: **{st.session_state.v2.cliente_actual.nombre}**")

        autos_restantes = [c.nombre for c in st.session_state.cola_autos]
        if autos_restantes:
            box_cola.success(" ──> ".join([f"🐟 [{a}]" for a in autos_restantes]))
        else:
            box_cola.warning("🛑 Fondo de Bikini está satisfecho.")

        tickets_impresos = list(st.session_state.pila_tickets)
        if tickets_impresos:
            with box_pila.container(border=True):
                for tk in reversed(tickets_impresos):
                    st.text(f"🧾 Orden de {tk.nombre} - Total: ${tk.total:.2f}")
        else:
            box_pila.caption("Esperando primer ticket...")

        dinero_actual = sum(tk.total for tk in tickets_impresos)
        box_caja.metric(label="💵 Venta Acumulada", value=f"${dinero_actual:.2f}")
        
        time.sleep(0.3)

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡El caos ha sido resuelto de manera ordenada!")
