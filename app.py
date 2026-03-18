import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.quantum_info import Statevector
from qiskit_aer.noise import NoiseModel, depolarizing_error

# Page Config
st.set_page_config(page_title="Quantum Circuit Playground", layout="wide")

st.title("⚛️ Quantum Circuit Playground")
st.write("Explore Bell States, GHZ States, and Quantum Teleportation")

# Sidebar
option = st.sidebar.selectbox(
    "Choose Experiment",
    ["Bell State", "GHZ State", "Quantum Teleportation"]
)

shots = st.sidebar.slider("Shots", 100, 5000, 1024)

use_noise = st.sidebar.checkbox("Enable Noise (Realistic Simulation)")

# Backend
backend = Aer.get_backend('aer_simulator')

# Noise Model
noise_model = None
if use_noise:
    noise_model = NoiseModel()
    # 1-qubit error
    error_1 = depolarizing_error(0.05, 1)
    # 2-qubit error
    error_2 = depolarizing_error(0.05, 2)
    # Apply correctly
    noise_model.add_all_qubit_quantum_error(error_1, ['h'])
    noise_model.add_all_qubit_quantum_error(error_2, ['cx'])


# -------------------------------
# Utility: Download Results
# -------------------------------
def download_counts(counts):
    df = pd.DataFrame(counts.items(), columns=["State", "Count"])
    st.download_button("⬇ Download Results", df.to_csv(index=False), "results.csv")


# -------------------------------
# Bell State
# -------------------------------
def bell_state():
    st.header("🔗 Bell State")

    with st.expander("📘 Explanation"):
        st.write("""
        - Hadamard creates superposition
        - CNOT entangles qubits
        - Result: 50% |00⟩ and 50% |11⟩
        """)

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)

    # Bloch sphere BEFORE measurement
    state = Statevector.from_instruction(qc)
    st.subheader("Bloch Sphere")
    st.pyplot(plot_bloch_multivector(state))

    qc.measure([0, 1], [0, 1])

    st.subheader("Circuit")
    st.pyplot(qc.draw('mpl'))

    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots, noise_model=noise_model)
    result = job.result()
    counts = result.get_counts()

    st.subheader("Measurement Results")
    st.pyplot(plot_histogram(counts))

    download_counts(counts)


# -------------------------------
# GHZ State
# -------------------------------
def ghz_state():
    st.header("🌐 GHZ State")

    n = st.slider("Number of Qubits", 3, 6, 3)

    with st.expander("📘 Explanation"):
        st.write("""
        - Extends Bell state to multiple qubits
        - Creates global entanglement
        """)

    qc = QuantumCircuit(n, n)
    qc.h(0)

    for i in range(n - 1):
        qc.cx(i, i + 1)

    # Bloch Sphere
    state = Statevector.from_instruction(qc)
    st.subheader("Bloch Sphere")
    st.pyplot(plot_bloch_multivector(state))

    qc.measure(range(n), range(n))

    st.subheader("Circuit")
    st.pyplot(qc.draw('mpl'))

    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots, noise_model=noise_model)
    result = job.result()
    counts = result.get_counts()

    st.subheader("Measurement Results")
    st.pyplot(plot_histogram(counts))

    download_counts(counts)


# -------------------------------
# Quantum Teleportation
# -------------------------------
def teleportation():
    st.header("📡 Quantum Teleportation")

    with st.expander("📘 Explanation"):
        st.write("""
        - Transfers quantum state without moving particle
        - Uses entanglement + classical communication
        """)

    qc = QuantumCircuit(3, 3)

    # Initial state
    qc.h(0)

    # Save initial state
    init_state = Statevector.from_instruction(qc)

    st.subheader("Initial State (Bloch Sphere)")
    st.pyplot(plot_bloch_multivector(init_state))

    # Bell pair
    qc.h(1)
    qc.cx(1, 2)

    # Entangle
    qc.cx(0, 1)
    qc.h(0)

    qc.measure([0, 1], [0, 1])

    # Conditional corrections
    qc.cx(1, 2)
    qc.cz(0, 2)

    qc.measure(2, 2)

    st.subheader("Circuit")
    st.pyplot(qc.draw('mpl'))

    compiled = transpile(qc, backend)
    job = backend.run(compiled, shots=shots, noise_model=noise_model)
    result = job.result()
    counts = result.get_counts()

    st.subheader("Measurement Results")
    st.pyplot(plot_histogram(counts))

    st.success("Quantum state teleported successfully!")

    download_counts(counts)


# -------------------------------
# Run App
# -------------------------------
if option == "Bell State":
    bell_state()

elif option == "GHZ State":
    ghz_state()

elif option == "Quantum Teleportation":
    teleportation()
