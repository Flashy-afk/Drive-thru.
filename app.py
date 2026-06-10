# app.py
import streamlit as st
import time
from collections import deque
from producto import Producto
from cliente import Cliente
# Importa aquí tu clase CajeroVisual (o déjala definida arriba)

st.set_page_config(page_title="Carl's Jr. Drive-Thru", layout="wide")
st.title("🍔 Carl's Jr. — Drive-Thru Simulación")

# --- INICIALIZACIÓN SEGURA ---
if 'simulacion_activa' not in st.session_state:
    st.session_state.simulacion_activa = False
    st.session_state.cola_autos = deque()
    st.session_state.pila_tickets = []

# --- LÓGICA DE INICIO ---
if not st.session_state.simulacion_activa:
    if st.button("🚀 Iniciar Emulación"):
        nombres = ["Parra", "Casas", "Pablo", "Fernanda", "Jonathan", "Cisthian", "Luz", "Kevin"]
        st.session_state.cola_autos = deque([Cliente(n) for n in nombres])
        # Iniciar hilos
        st.session_state.v1 = CajeroVisual("VENTANILLA 1", st.session_state.cola_autos, [...], st.session_state.pila_tickets)
        st.session_state.v2 = CajeroVisual("VENTANILLA 2", st.session_state.cola_autos, [...], st.session_state.pila_tickets)
        st.session_state.v1.start()
        st.session_state.v2.start()
        st.session_state.simulacion_activa = True
        st.rerun() # Reinicia el script para entrar al modo de visualización

# --- VISUALIZACIÓN (SIN BUCLE WHILE) ---
if st.session_state.simulacion_activa:
    # 1. Layout (esto se dibuja una sola vez)
    col_izq, col_der = st.columns([2, 1])
    # ... (dibuja tus contenedores vacíos con st.empty() aquí) ...
    
    # 2. Actualización de UI
    # En lugar de while, actualizamos componentes y luego dormimos brevemente
    # y forzamos un rerender
    
    # ... (tu lógica para actualizar box_v1, box_v2, etc.) ...
    
    time.sleep(0.3)
    if st.session_state.v1.is_alive() or st.session_state.v2.is_alive():
        st.rerun() # Esto le dice a Streamlit: "dibuja de nuevo con los nuevos valores"
    else:
        st.session_state.simulacion_activa = False
        st.success("¡Simulación finalizada!")
