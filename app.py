import streamlit as st
import time
import threading
from collections import deque
from producto import Producto
from cliente import Cliente

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Carl's Jr. Drive-Thru", layout="wide")

# --- INICIALIZACIÓN ---
if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.lock = threading.Lock()

# --- INTERFAZ ---
st.title("🍔 Carl's Jr. - Simulación de Alto Rendimiento")

if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Flujo de Simulación"):
        nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        st.session_state.simulacion_activa = True
        st.rerun()

# --- RENDERIZADO (SIN BUCLE INFINITO) ---
if st.session_state.simulacion_activa:
    # 1. Definimos un contenedor donde se dibujará todo
    mapa_placeholder = st.empty()
    
    # 2. Lógica de "animación" sin bloquear
    with mapa_placeholder.container():
        st.markdown("""
        <div style="background:#4CAF50; padding:20px; border-radius:10px; color:white;">
            <h3>Escena de Simulación</h3>
            <p>Aquí se visualizarán los autos moviéndose.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulamos un paso de la lógica
        st.write("Procesando vehículos...")
        
    # 3. Refresco controlado: Streamlit se encarga de redibujar la UI
    # al finalizar este script, sin necesidad de un while True bloqueante.
    time.sleep(0.5) 
    st.rerun()
