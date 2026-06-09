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
        self.estado = "☕ Esperando auto..."
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
            self.estado = f"✅ ¡Listo! ${cliente.total:.1f}"
            self.pila_tickets.append(cliente)
            time.sleep(1.2)
            
        self.cliente_actual = None
        self.estado = "☕ Esperando auto..."
        self.progreso = 0

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Carl's Jr. Top-Down Drive-Thru", page_icon="🍔", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    .mapa-container {
        background-color: #2e7d32;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }
    .zona-ventanillas {
        display: flex;
        justify-content: space-around;
        margin-bottom: 5px;
    }
    .caja-ventanilla {
        background-color: #ffffff;
        border: 4px solid #ffcc00;
        border-radius: 12px;
        width: 45%;
        padding: 10px;
        box-shadow: 0px 6px 10px rgba(0,0,0,0.15);
    }
    .titulo-ventanilla {
        font-weight: bold;
        font-size: 15px;
        color: #111;
        margin-bottom: 5px;
    }
    .asfalto-servicio {
        background-color: #3a3a3a;
        min-height: 70px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px dashed #ffcc00;
        margin-top: 5px;
    }
    .auto-activo {
        background-color: #e53935;
        color: white;
        padding: 8px 18px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
    }
    .spot-vacio {
        color: #aaa;
        font-size: 13px;
        font-style: italic;
    }
    .lineas-division {
        font-size: 24px;
        color: #fff;
        margin: 5px 0;
        line-height: 14px;
        font-weight: bold;
    }
    .carril-acceso {
        background-color: #2c2c2c;
        border-radius: 12px;
        padding: 15px;
        border-left: 4px dashed #ffcc00;
        border-right: 4px dashed #ffcc00;
        max-width: 400px;
        margin: 0 auto;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.3);
    }
    .titulo-carril {
        color: #ffcc00;
        font-size: 11px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 12px;
        letter-spacing: 2px;
    }
    .flujo-autos {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 12px;
    }
    .auto-fila {
        background-color: #1e88e5;
        color: white;
        padding: 8px 0;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
        width: 85%;
        box-shadow: 0px 4px 5px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🍔 Carl's Jr. — Croquis del Drive-Thru desde Arriba")
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
        if st.button("🚀 Encender Motores y Simular Fila", type="primary", use_container_width=True):
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
        st.subheader("🗺️ Mapa del Establecimiento (Perspectiva Aérea)")
        contenedor_mapa_vivo = st.empty()

    with col_reporte:
        st.subheader("🧾 Historial de Caja (Pila - LIFO)")
        box_pila = st.empty()
        box_caja = st.empty()

    while st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        v1_html = f"<div class='auto-activo'>🚗 {st.session_state.v1.cliente_actual.nombre}</div>" if st.session_state.v1.cliente_actual else "<span class='spot-vacio'>Vacio 🪹</span>"
        v2_html = f"<div class='auto-activo'>🚗 {st.session_state.v2.cliente_actual.nombre}</div>" if st.session_state.v2.cliente_actual else "<span class='spot-vacio'>Vacio 🪹</span>"

        autos_carrril_html = ""
        for auto in st.session_state.cola_autos:
            autos_carrril_html += f"<div class='auto-fila'>🚗 {auto.nombre}</div>"
        if not autos_carrril_html:
            autos_carrril_html = "<div style='color: #aaa; font-style: italic; font-size:13px;'>Carril despejado</div>"

        # Plantilla compacta sin saltos de línea vacíos
        mapa_completo_html = f"""<div class='mapa-container'><div class='zona-ventanillas'><div class='caja-ventanilla'><div class='titulo-ventanilla'>🪟 Ventanilla 1</div><div style='font-size:12px; color:#666;'>{st.session_state.v1.estado}</div><div class='asfalto-servicio'>{v1_html}</div></div><div class='caja-ventanilla'><div class='titulo-ventanilla'>🪟 Ventanilla 2</div><div style='font-size:12px; color:#666;'>{st.session_state.v2.estado}</div><div class='asfalto-servicio'>{v2_html}</div></div></div><div class='lineas-division'>↖  ↗<br>│  │<br>└──┴──<br>▲</div><div class='carril-acceso'><div class='titulo-carril'>🛣️ Fila Única de Acceso</div><div class='flujo-autos'>{autos_carrril_html}</div></div></div>"""
        
        contenedor_mapa_vivo.markdown(mapa_completo_html, unsafe_allow_html=True)

        tickets_list = list(st.session_state.pila_tickets)
        with box_pila.container(border=True):
            if tickets_list:
                for tk in reversed(tickets_list):
                    st.write(f"📌 **Ticket de {tk.nombre}** — Finalizado con ${tk.total:.2f}")
            else:
                st.caption("Esperando cierres de orden...")

        caja_total = sum(tk.total for tk in tickets_list)
        box_caja.metric(label="💰 Dinero Total Acumulado en Caja", value=f"${caja_total:.2f}")

        time.sleep(0.2)

    st.session_state.simulacion_activa = False
    st.balloons()
    st.success("🎉 ¡El turno ha terminado con éxito! Todos los vehículos cruzaron el Drive-Thru.")
