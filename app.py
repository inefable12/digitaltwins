import streamlit as st
import simpy
import random
import numpy as np

st.title("Digital Twins para Atención Hospitalaria")
st.


import streamlit as st
import random
import simpy
import numpy as np

# Configuración inicial para Streamlit
st.title("Simulación del Sistema de Entrega de Medicamentos en un Hospital")

# Entrada de parámetros desde la interfaz
RANDOM_SEED = st.sidebar.number_input("Semilla Aleatoria (RANDOM_SEED)", value=42, step=1)
NUM_CAMAS = st.sidebar.number_input("Número de Camas (NUM_CAMAS)", value=100, step=1)
OCUPACION_INICIAL = st.sidebar.number_input("Ocupación Inicial (OCUPACION_INICIAL)", value=90, step=1)
HORAS_SIMULACION = st.sidebar.number_input("Horas de Simulación (HORAS_SIMULACION)", value=12, step=1)
INTERVALO_ALTAS = st.sidebar.slider("Intervalo de Altas Médicas (INTERVALO_ALTAS)", 0, 100, (20, 40))
TIEMPO_SOLICITUD_RECEPCION = st.sidebar.slider("Tiempo de Solicitud y Recepción (TIEMPO_SOLICITUD_RECEPCION)", 0, 60, (10, 25))
TIEMPO_PREPARACION = st.sidebar.slider("Tiempo de Preparación (TIEMPO_PREPARACION)", 0, 60, (20, 30))
TIEMPO_RECOJO = st.sidebar.slider("Tiempo de Recojo (TIEMPO_RECOJO)", 0, 120, (30, 60))
NUM_SIMULACIONES = st.sidebar.number_input("Número de Simulaciones (NUM_SIMULACIONES)", value=10000, step=1)

# Simulación con SimPy
def paciente(env, tiempos1, tiempos2, tiempos3, farmacia):
    """Proceso que simula a un paciente recogiendo medicamentos."""
    tiempo1 = random.uniform(*TIEMPO_SOLICITUD_RECEPCION)
    yield env.timeout(tiempo1)
    tiempos1.append(tiempo1)

    with farmacia.request() as req:
        yield req
        tiempo2 = random.uniform(*TIEMPO_PREPARACION)
        yield env.timeout(tiempo2)
        tiempos2.append(tiempo2)

    tiempo3 = random.uniform(*TIEMPO_RECOJO)
    yield env.timeout(tiempo3)
    tiempos3.append(tiempo3)

def generar_altas(env, tiempos1, tiempos2, tiempos3, farmacia):
    """Genera pacientes dados de alta diariamente."""
    while True:
        yield env.timeout(3)
        num_altas = random.randint(*INTERVALO_ALTAS)
        for _ in range(num_altas):
            env.process(paciente(env, tiempos1, tiempos2, tiempos3, farmacia))

def simulacion():
    """Ejecuta una simulación."""
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    farmacia = simpy.Resource(env, capacity=3)
    tiempos1, tiempos2, tiempos3 = [], [], []
    env.process(generar_altas(env, tiempos1, tiempos2, tiempos3, farmacia))
    env.run(until=HORAS_SIMULACION * 60)
    return tiempos1, tiempos2, tiempos3

# Ejecutar simulaciones
if st.button("Ejecutar Simulación"):
    tiempos1_totales, tiempos2_totales, tiempos3_totales = [], [], []
    for _ in range(NUM_SIMULACIONES):
        t1, t2, t3 = simulacion()
        tiempos1_totales.extend(t1)
        tiempos2_totales.extend(t2)
        tiempos3_totales.extend(t3)

    # Resultados
    st.header("Resultados de la Simulación")
    st.write(f"Tiempo 1 Promedio: {np.mean(tiempos1_totales):.2f} minutos")
    st.write(f"Tiempo 2 Promedio: {np.mean(tiempos2_totales):.2f} minutos")
    st.write(f"Tiempo 3 Promedio: {np.mean(tiempos3_totales):.2f} minutos")

    # Visualización
    st.subheader("Distribución de los Tiempos")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    axes[0].hist(tiempos1_totales, bins=30, color='blue', alpha=0.7, density=True)
    axes[0].set_title("Tiempo 1")
    axes[0].set_xlabel("Minutos")
    axes[0].set_ylabel("Frecuencia")

    axes[1].hist(tiempos2_totales, bins=30, color='green', alpha=0.7, density=True)
    axes[1].set_title("Tiempo 2")
    axes[1].set_xlabel("Minutos")

    axes[2].hist(tiempos3_totales, bins=30, color='red', alpha=0.7, density=True)
    axes[2].set_title("Tiempo 3")
    axes[2].set_xlabel("Minutos")

    plt.tight_layout()
    st.pyplot(fig)
