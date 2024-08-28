import socket

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st


# Função alulol gayyy para converter texto em bits ASCII
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
st.title("Modulação NRZ-Polar, Manchester, Bipolar, Portadora, ASK , FSK e 8-QAM")

def modulacao(bits):
    constelacao = {
            (0, 0, 0): complex(-1, -1), #0
            (0, 0, 1): complex(-1, 1),  #1
            (0, 1, 0): complex(1, -1),  #2
            (0, 1, 1): complex(1, 1),   #3
            (1, 0, 0): complex(-1, -3), #4
            (1, 0, 1): complex(-1, 3),  #5
            (1, 1, 0): complex(1, -3),  #6
            (1, 1, 1): complex(1, 3)    #7
            }

    bits = np.append(bits, [0] * (3 - len(bits) % 3) if len(bits) % 3 != 0 else [])
    tam = len(bits)
    if tam % 3 != 0:
        while tam % 3 != 0:
            bits.append(0)

    # Converte bits em símbolos 8QAM de forma menos eficiente
    bits_simbolos = []
    for i in range(0, len(bits), 3):
        # Cria uma tupla manualmente de 3 em 3 bits
        simbolo = (bits[i], bits[i+1] if i+1 < len(bits) else 0, bits[i+2] if i+2 < len(bits) else 0)
        bits_simbolos.append(simbolo)

    # Inicializa uma lista vazia para armazenar os símbolos modulados
    simbolos_modulados = []
    for simbolo in bits_simbolos:
        # Adiciona cada símbolo mapeado à lista manualmente
        simbolos_modulados.append(constelacao[simbolo])

    # Retorna a lista de símbolos modulados
    return banda_base_8qam(simbolos_modulados)

def banda_base_8qam(simbolos_modulados):
    duracao_simbolo = 1 / 8  # Duração de cada símbolo
    num_simbolos = len(simbolos_modulados)
    
    # Vetor de tempo para um símbolo
    tempo_simbolo = np.linspace(0, duracao_simbolo, 100)
    
    # Vetor de tempo total
    tempo_total = np.linspace(0, duracao_simbolo * num_simbolos, num_simbolos * 100)

    # Inicializa a forma de onda como um array de zeros, com tipo complexo para suportar parte real e imaginária
    forma_onda = np.zeros(len(tempo_total), dtype=complex)

    for i in range(num_simbolos):
        inicio = i * 100
        fim = (i + 1) * 100
        
        # Obter o símbolo atual
        simbolo = simbolos_modulados[i]
        
        # Modula o sinal e armazena na forma de onda (usando a função exponencial complexa)
        forma_onda[inicio:fim] = simbolo * np.exp(1j * 2 * np.pi * 24 * tempo_simbolo)

    return forma_onda

# Streamlit UI setup
st.title("Modulação e Envio de Mensagens")

# Persistent connection setup
if 'client_socket' not in st.session_state:
    st.session_state.client_socket = None

# Input for nickname and message
nickname = st.text_input("Digite seu apelido:")
text = st.text_input("Digite o texto:")

if st.button("Conectar ao servidor"):
    if not st.session_state.client_socket:
        try:
            st.session_state.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            st.session_state.client_socket.connect(('192.168.15.166', 5060))  # Replace with your server IP and port if needed
            st.success("Conectado ao servidor com sucesso!")
        except Exception as e:
            st.error(f"Erro ao conectar ao servidor: {e}")

if st.button("Enviar apelido"):
    if not nickname:
        st.warning("Por favor, insira um apelido.")
    elif st.session_state.client_socket:
        try:
            st.session_state.client_socket.send(nickname.encode('ascii'))
            st.success("Apelido enviado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar o apelido para o servidor: {e}")
    else:
        st.error("Você deve se conectar ao servidor primeiro.")

if st.button("Enviar mensagem"):
    if not text:
        st.warning("Por favor, insira um texto.")
    elif st.session_state.client_socket:
        try:
            st.session_state.client_socket.send(text.encode('ascii'))
            st.success("Mensagem enviada com sucesso!")
        except Exception as e:
            st.error(f"Erro ao enviar a mensagem para o servidor: {e}")
    else:
        st.error("Você deve se conectar ao servidor primeiro.")

if text:
    ascii_bits = text_to_bits(text)
    st.write("Vetor ASCII de cada letra:")
    for i, char_bits in enumerate(ascii_bits):
        st.write(f"{text[i]}: {char_bits}")

    bits = ''.join(ascii_bits)

    modulation_type = st.selectbox("Escolha o tipo de modulação", ["Digital", "Portadora"])

    if modulation_type == "Digital":
        modulation_scheme = st.selectbox("Escolha a técnica de modulação digital", ["NRZ-Polar", "Manchester", "Bipolar"])
    else:
        modulation_scheme = st.selectbox("Escolha a técnica de modulação por portadora", ["ASK", "FSK"])

    if st.button("Modular"):
        if bits:
            freq = 1
            t = np.linspace(0, len(bits), len(bits) * 100)
            clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))

            carrier_freq = freq
            carrier = np.sin(2 * np.pi * carrier_freq * t)

            fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

            axs[0].plot(t, np.repeat(list(map(int, bits)), 100), drawstyle='steps-pre')
            axs[0].set(title="Entrada", ylabel="Bit")
            axs[0].grid(True)
            axs[0].legend(["Entrada"])

            axs[1].plot(t, clock, drawstyle='steps-pre')
            axs[1].set(title="Clock", ylabel="Amplitude")
            axs[1].grid(True)
            axs[1].legend(["Clock"])

            if modulation_type == "Digital":
                if modulation_scheme == "NRZ-Polar":
                    signal = nrz_polar(bits)
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
                    signal_bipolar = bipolar(bits)
                    signal_expanded_bipolar = np.repeat(signal_bipolar, 100)
                    axs[2].plot(t, signal_expanded_bipolar, drawstyle='steps-pre')
                    axs[2].set(title="Bipolar Modulation", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["Bipolar"])

            else:
                signal = nrz_polar(bits)

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