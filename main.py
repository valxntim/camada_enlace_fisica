import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

#valentao seu botafogo vai cair!!!

# Função para converter texto em bits ASCII
def text_to_bits(text):
    # Converte cada caractere do texto em sua representação binária de 8 bits
    bits = [format(ord(char), '08b') for char in text]
    return bits

# Função para modulação NRZ-Polar
def nrz_polar(bits):
    signal = []  # Lista de bits
    for bit in bits:
        if bit == '0':  # Bits 0 e 1 são representados por -1 e 1
            signal.append(-1)
        else:
            signal.append(1)
    return signal

# Função para modulação Manchester
def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)  # Recebe o sinal NRZ-Polar
    nrz_expanded = np.repeat(nrz_signal, 100)  # Repete o sinal para 100 vezes cada elemento da lista, [0,1] vira [0,0,0,0...,1,1,1,1...]
    manchester_signal = np.logical_xor(nrz_expanded > 0, clock > 0.5).astype(int)
    manchester_signal = manchester_signal * 2 - 1  # Ajusta os valores para -1 e 1
    return manchester_signal

# Função para modulação Bipolar
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

# Função para modulação ASK
def ask_modulation(nrz_signal, carrier):
    # Expande o sinal NRZ para combinar com a frequência do portador
    nrz_expanded = np.repeat(nrz_signal, 100)
    # Modula o sinal portador com base no sinal NRZ
    ask_signal = np.where(nrz_expanded == 1, carrier, 0)
    return ask_signal

# Função para modulação FSK
def fsk_modulation(nrz_signal, t, carrier_freq):
    # Expande o sinal NRZ para combinar com a frequência do portador
    nrz_expanded = np.repeat(nrz_signal, 100)
    # Define frequências para FSK
    freq_high = carrier_freq * 2
    freq_low = carrier_freq
    # Modula o sinal com FSK
    fsk_signal = np.where(nrz_expanded == 1, np.sin(2 * np.pi * freq_high * t), np.sin(2 * np.pi * freq_low * t))
    return fsk_signal

# Configuração do Streamlit
st.title("Modulação NRZ-Polar, Manchester, Bipolar, Portadora, ASK e FSK")

# Entrada do usuário
input_type = st.selectbox("Escolha o tipo de entrada", ["Bits", "Texto"])
if input_type == "Bits":
    bits = st.text_input("Digite os bits (ex: 10110011):")
else:
    text = st.text_input("Digite o texto:")
    if text:
        ascii_bits = text_to_bits(text)
        bits = ''.join(ascii_bits)
        st.write("Vetor ASCII de cada letra:")
        for i, char_bits in enumerate(ascii_bits):
            st.write(f"{text[i]}: {char_bits}")
    else:
        bits = ""

# Seleção do tipo de modulação
modulation_type = st.selectbox("Escolha o tipo de modulação", ["Digital", "Portadora"])

# Seleção da técnica de modulação específica
if modulation_type == "Digital":
    modulation_scheme = st.selectbox("Escolha a técnica de modulação digital", ["NRZ-Polar", "Manchester", "Bipolar"])
else:
    modulation_scheme = st.selectbox("Escolha a técnica de modulação por portadora", ["ASK", "FSK"])

if st.button("Modular"):
    if bits:  # Se o usuário digitou algum valor
        # Frequência do clock ajustada para ter transições claras
        freq = 1  # Frequência do clock ajustada para 1 Hz ou seja em 1 segundo teremos uma transição de 0 para 1 ou 1 para 0, período igual a 1 segundo
        t = np.linspace(0, len(bits), len(bits) * 100)  # Gerando o tempo para o sinal, ou seja ele vai de 0 ao tamanho do sinal ou seja se eu tenho 5 bits ele vai de 0 a 5 segundos e criamos 100 pontos para cada um deles igualmente espaçados
        clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))
        
        # Gerar sinal portadora
        carrier_freq = freq  # Frequência da portadora igual à do clock
        carrier = np.sin(2 * np.pi * carrier_freq * t)

        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

        # Plotando a entrada
        axs[0].plot(t, np.repeat(list(map(int, bits)), 100), drawstyle='steps-pre')
        axs[0].set(title="Entrada", ylabel="Bit")
        axs[0].grid(True)
        axs[0].legend(["Entrada"])

        # Plotando o clock
        axs[1].plot(t, clock, drawstyle='steps-pre')
        axs[1].set(title="Clock", ylabel="Amplitude")
        axs[1].grid(True)
        axs[1].legend(["Clock"])

        # Modulação digital
        if modulation_type == "Digital":
            if modulation_scheme == "NRZ-Polar":
                signal = nrz_polar(bits)  # Sinal que o usuário digitou vai ser convertido para NRZ-Polar
                signal_expanded = np.repeat(signal, 100)
                axs[2].plot(t, signal_expanded, drawstyle='steps-pre')
                axs[2].set(title="NRZ-Polar Modulation", xlabel="Tempo", ylabel="Amplitude")
                axs[2].legend(["NRZ-Polar"])

            elif modulation_scheme == "Manchester":
                manchester_signal = manchester(bits, clock)
                axs[2].plot(t, manchester_signal, drawstyle='steps-pre')
                axs[2].set(title="Manchester Encoding", xlabel="Tempo", ylabel="Amplitude")
                axs[2].legend(["Manchester"])

            elif modulation_scheme == "Bipolar":
                signal_bipolar = bipolar(bits)  # Sinal que o usuário digitou vai ser convertido para Bipolar
                signal_expanded_bipolar = np.repeat(signal_bipolar, 100)
                axs[2].plot(t, signal_expanded_bipolar, drawstyle='steps-pre')
                axs[2].set(title="Bipolar Modulation", xlabel="Tempo", ylabel="Amplitude")
                axs[2].legend(["Bipolar"])

        # Modulação por portadora
        else:
            signal = nrz_polar(bits)  # Sinal que o usuário digitou vai ser convertido para NRZ-Polar

            if modulation_scheme == "ASK":
                ask_signal = ask_modulation(signal, carrier)
                axs[2].plot(t, ask_signal, drawstyle='steps-pre')
                axs[2].set(title="ASK Modulated Signal", xlabel="Tempo", ylabel="Amplitude")
                axs[2].legend(["ASK"])

            elif modulation_scheme == "FSK":
                fsk_signal = fsk_modulation(signal, t, carrier_freq)
                axs[2].plot(t, fsk_signal, drawstyle='steps-pre')
                axs[2].set(title="FSK Modulated Signal", xlabel="Tempo", ylabel="Amplitude")
                axs[2].legend(["FSK"])

        axs[2].grid(True)
        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits ou um texto.")
