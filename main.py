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

def generate_square_wave(length, freq=60):
    # O período da onda quadrada é 1/freq, então para 60 Hz é 1/60 segundos por ciclo
    # Cada ciclo tem 0.5 ON e 0.5 OFF, então a frequência do clock é metade disso
    period = 1 / freq
    t = np.arange(0, length, period / 2)
    clock = np.array([(i % 2) for i in range(len(t))])
    return t, clock

st.title("Modulação NRZ-Polar")

bits = st.text_input("Digite os bits (ex: 10110011):")

if st.button("Modular"):
    if bits:
        length = len(bits)
        signal = nrz_polar(bits)
        t, clock = generate_square_wave(length * 2, freq=2)  # Frequência ajustada para 2 Hz para onda quadrada

        # Cria sinais para entrada de bits e saída NRZ-Polar alinhados com o clock
        bit_signal = []
        nrz_signal = []
        for i in range(len(clock)):
            if clock[i] == 1:  # Clock está "ON"
                bit_index = i // 2
                if bit_index < len(bits):
                    bit_signal.append(int(bits[bit_index]))
                    nrz_signal.append(signal[bit_index])
                else:
                    bit_signal.append(0)
                    nrz_signal.append(0)
            else:  # Clock está "OFF"
                bit_signal.append(0)
                nrz_signal.append(0)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 6), sharex=True)

        ax1.plot(t, bit_signal, drawstyle='steps-pre')
        ax1.set(title="Entrada de Bits", ylabel="Bits")
        ax1.grid(True)

        ax2.plot(t, clock, drawstyle='steps-pre')
        ax2.set(title="Clock", ylabel="Clock")
        ax2.grid(True)

        ax3.plot(t, nrz_signal, drawstyle='steps-pre')
        ax3.set(title="NRZ-Polar Modulation", xlabel="Tempo", ylabel="Amplitude")
        ax3.grid(True)

        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits.")
