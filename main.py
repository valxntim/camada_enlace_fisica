import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


def nrz_polar(bits):
    signal = []         #  Lista de  bits
    for bit in bits:
        if bit == '0':  #  Bits 0 e 1 são representados por -1 e 1
            signal.append(-1)
        else:
            signal.append(1)
    return signal

def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)    #Recebe o sinal NRZ-Polar
    nrz_expanded = np.repeat(nrz_signal, 100)  #Repete o sinal para 100 vezes cada elemento da lista, [0,1] vira [0,0,0,0...,1,1,1,1...]
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

def ask_modulation(nrz_signal, carrier):
    # Expande o sinal NRZ para combinar com a frequência do portador
    nrz_expanded = np.repeat(nrz_signal, 100)
    # Modula o sinal portador com base no sinal NRZ
    ask_signal = np.where(nrz_expanded == 1, carrier, 0)
    return ask_signal

def fsk_modulation(nrz_signal, t, carrier_freq):
    # Expande o sinal NRZ para combinar com a frequência do portador
    nrz_expanded = np.repeat(nrz_signal, 100)
    # Define frequências para FSK
    freq_high = carrier_freq * 2
    freq_low = carrier_freq
    # Modula o sinal com FSK
    fsk_signal = np.where(nrz_expanded == 1, np.sin(2 * np.pi * freq_high * t), np.sin(2 * np.pi * freq_low * t))
    return fsk_signal

st.title("Modulação NRZ-Polar, Manchester, Bipolar, Portadora, ASK e FSK")

bits = st.text_input("Digite os bits (ex: 10110011):")

if st.button("Modular"):
    if bits:    # Se o usuário digitou algum valor
        signal = nrz_polar(bits)    #sinal que o usuário digitou vai ser convertido para NRZ-Polar
        signal_bipolar = bipolar(bits)  #sinal que o usuário digitou vai ser convertido para Bipolar
        
        # Frequência do clock ajustada para ter transições claras
        freq = 1  # Frequência do clock ajustada para 1 Hz ou seja em 1 segundo teremos uma transição de 0 para 1 ou 1 para 0, periodo igual a 1 segundo
        t = np.linspace(0, len(bits), len(bits) * 100)  # Gerando o tempo para o sinal, ou seja ele vai de 0 a o tamanho do sinal  ou seja se eu tenho 5 bits ele vai de 0 a 5 segundos e criamos 100 pontos para cada um deles igualmente espacados
        clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))
        
        # Gerar sinal portadora
        carrier_freq = freq  # Frequência da portadora igual à do clock
        carrier = np.sin(2 * np.pi * carrier_freq * t)

        # Ajustando o sinal de acordo com o clock
        signal_expanded = np.repeat(signal, 100)
        signal_expanded_bipolar = np.repeat(signal_bipolar, 100)

        # Gerando sinal Manchester
        manchester_signal = manchester(bits, clock)

        # Gerando sinal ASK
        ask_signal = ask_modulation(signal, carrier)

        # Gerando sinal FSK
        fsk_signal = fsk_modulation(signal, t, carrier_freq)

        fig, axs = plt.subplots(8, 1, figsize=(10, 14), sharex=True)
        
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

        # Plotando a portadora
        axs[5].plot(t, carrier, drawstyle='steps-pre')
        axs[5].set(title="Carrier Signal", xlabel="Tempo", ylabel="Amplitude")
        axs[5].grid(True)
        axs[5].legend(["Carrier"])

        # Plotando a saída ASK
        axs[6].plot(t, ask_signal, drawstyle='steps-pre')
        axs[6].set(title="ASK Modulated Signal", xlabel="Tempo", ylabel="Amplitude")
        axs[6].grid(True)
        axs[6].legend(["ASK"])

        # Plotando a saída FSK
        axs[7].plot(t, fsk_signal, drawstyle='steps-pre')
        axs[7].set(title="FSK Modulated Signal", xlabel="Tempo", ylabel="Amplitude")
        axs[7].grid(True)
        axs[7].legend(["FSK"])

        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits.")
