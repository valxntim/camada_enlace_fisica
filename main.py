import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def nrz_polar(bits):
    signal = []
    for bit in bits:
        if bit == '0':
            signal.append(-1)
        else:
            signal.append(1)
    return signal

def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)
    nrz_expanded = np.repeat(nrz_signal, 100)
    manchester_signal = np.logical_xor(nrz_expanded > 0, clock > 0.5).astype(int)
    manchester_signal = manchester_signal * 2 - 1  # Ajusta os valores para -1 e 1
    return manchester_signal

st.title("Modulação NRZ-Polar e Manchester")

bits = st.text_input("Digite os bits (ex: 10110011):")

if st.button("Modular"):
    if bits:
        signal = nrz_polar(bits)
        
        # Frequência do clock ajustada para ter transições claras
        freq = 1  # Frequência do clock ajustada para 1 Hz
        t = np.linspace(0, len(bits), len(bits) * 100)
        clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))

        # Ajustando o sinal de acordo com o clock
        signal_expanded = np.repeat(signal, 100)

        # Gerando sinal Manchester
        manchester_signal = manchester(bits, clock)

        fig, axs = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
        
        # Plotando o clock
        axs[0].plot(t, clock, drawstyle='steps-pre')
        axs[0].set(title="Clock", ylabel="Amplitude")
        axs[0].grid(True)

        # Plotando a entrada
        axs[1].plot(t, np.repeat(list(map(int, bits)), 100), drawstyle='steps-pre')
        axs[1].set(title="Entrada", ylabel="Bit")
        axs[1].grid(True)

        # Plotando a saída NRZ
        axs[2].plot(t, signal_expanded, drawstyle='steps-pre')
        axs[2].set(title="NRZ-Polar Modulation", xlabel="Tempo", ylabel="Amplitude")
        axs[2].grid(True)

        # Plotando a saída Manchester
        axs[3].plot(t, manchester_signal, drawstyle='steps-pre')
        axs[3].set(title="Manchester Encoding", xlabel="Tempo", ylabel="Amplitude")
        axs[3].grid(True)

        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits.")
