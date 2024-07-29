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

def bipolar(bits):
    signal = []
    bits_um = None
    for bit in bits:
        if bit == '0':
            signal.append(0)
        else:
            if bits_um is None:
                bits_um = 1
                signal.append(bits_um)
            else:
                if bits_um == 1:
                    bits_um = -1
                    signal.append(bits_um)
                else:
                    bits_um = 1
                    signal.append(bits_um)
    return signal

st.title("Modulação NRZ-Polar, Manchester e Bipolar")

bits = st.text_input("Digite os bits (ex: 10110011):")

if st.button("Modular"):
    if bits:
        signal = nrz_polar(bits)
        signal_bipolar = bipolar(bits)
        # Frequência do clock ajustada para ter transições claras
        freq = 2  # Frequência do clock ajustada para 2 Hz
        t = np.linspace(0, len(bits), len(bits) * 100)
        clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))

        # Ajustando o sinal de acordo com o clock
        signal_expanded = np.repeat(signal, 100)
        signal_expanded_bipolar = np.repeat(signal_bipolar, 100)

        # Gerando sinal Manchester
        manchester_signal = manchester(bits, clock)

        fig, axs = plt.subplots(5, 1, figsize=(10, 8), sharex=True)
        
        # Plotando o clock
        axs[0].plot(t, clock, drawstyle='steps-pre')
        axs[0].set(title="Clock", ylabel="Amplitude")
        axs[0].grid(True)
        axs[0].legend(["Clock"])

        # Plotando a entrada
        axs[1].plot(t, np.repeat(list(map(int, bits)), 100), drawstyle='steps-pre')
        axs[1].set(title="Entrada", ylabel="Bit")
        axs[1].grid(True)
        axs[1].legend(["Entrada"])

        # Plotando a saída NRZ
        axs[2].plot(t, signal_expanded, drawstyle='steps-pre')
        axs[2].set(title="NRZ-Polar Modulation", xlabel="Tempo", ylabel="Amplitude")
        axs[2].grid(True)
        axs[2].legend(["NRZ-Polar"])

        # Plotando a saída Manchester
        axs[3].plot(t, manchester_signal, drawstyle='steps-pre')
        axs[3].set(title="Manchester Encoding", xlabel="Tempo", ylabel="Amplitude")
        axs[3].grid(True)
        axs[3].legend(["Manchester"])

        # Plotando a saída Bipolar
        axs[4].plot(t, signal_expanded_bipolar, drawstyle='steps-pre')
        axs[4].set(title="Bipolar Modulation", xlabel="Tempo", ylabel="Amplitude")
        axs[4].grid(True)
        axs[4].legend(["Bipolar"])

        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits.")
