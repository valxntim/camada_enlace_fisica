import socket
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import threading

# Initialize session state variables
if 'digital_modulation' not in st.session_state:
    st.session_state.digital_modulation = None

if 'carrier_modulation' not in st.session_state:
    st.session_state.carrier_modulation = None

if 'modulation_scheme' not in st.session_state:
    st.session_state.modulation_scheme = None

if 'bits' not in st.session_state:
    st.session_state.bits = None

if 'client_socket' not in st.session_state:
    st.session_state.client_socket = None

def signal_to_string(signal):
    return ','.join(str(bit) for bit in signal)

# Function to store modulation scheme
def set_modulation_scheme(selected_scheme):
    st.session_state.modulation_scheme = selected_scheme

# Function to convert text to ASCII bits
def text_to_bits(text):
    return [format(ord(char), '08b') for char in text]

# NRZ-Polar modulation function
def nrz_polar(bits):
    return [1 if bit == '1' else -1 for bit in bits]

# NRZ-Polar modulation function
def nrz_polar_demodulation(bits):
    return [1 if bit == '1' else 0 for bit in bits]

# Manchester modulation function with expanded clock
def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)
    nrz_expanded = np.repeat(nrz_signal, len(clock) // len(nrz_signal))
    manchester_signal = np.logical_xor(nrz_expanded > 0, clock > 0.5).astype(int)
    return manchester_signal * 2 - 1  # Convert Binary to Bipolar

# Bipolar modulation function
def bipolar(bits):
    signal = []
    last = -1
    for bit in bits:
        if bit == '1':
            last *= -1
            signal.append(last)
        else:
            signal.append(0)
    return signal

# ASK modulation function
def ask_modulation(nrz_signal, carrier):
    nrz_expanded = np.repeat(nrz_signal, len(carrier) // len(nrz_signal))
    return np.where(nrz_expanded == 1, carrier, 0)

# FSK modulation function
def fsk_modulation(nrz_signal, t, carrier_freq):
    nrz_expanded = np.repeat(nrz_signal, len(t) // len(nrz_signal))
    freq_high = carrier_freq * 2
    freq_low = carrier_freq
    return np.where(nrz_expanded == 1, np.sin(2 * np.pi * freq_high * t[:len(nrz_expanded)]), 
                               np.sin(2 * np.pi * freq_low * t[:len(nrz_expanded)]))

# 8-QAM modulation function
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

    tam = len(bits) 
    #print(tam)
    if tam % 3 != 0:
        while tam % 3 != 0:
            bits.append(0)
            tam = len(bits)
    tam = len(bits)
    #print(tam)
    # Converte bits em símbolos 8QAM 
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
    duracao_simbolo = 3  # Duração de cada símbolo
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
        forma_onda[inicio:fim] = simbolo * np.exp(1j * 2 * np.pi * 1 * tempo_simbolo)

    #print(forma_onda)
    return forma_onda

# Function to listen for incoming messages from the server
def listen_for_messages():
    while True:
        try:
            message = st.session_state.client_socket.recv(1048576).decode('ascii')
            if message:
                st.session_state.received_messages.append(message)
                st.experimental_rerun()
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

# Streamlit UI setup
st.title("Modulação e Envio de Mensagens")

# Input for nickname and message
nickname = st.text_input("Digite seu apelido:")
text = st.text_input("Digite o texto:")

if st.button("Conectar ao servidor"):
    if not st.session_state.client_socket:
        try:
            st.session_state.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            st.session_state.client_socket.connect(('192.168.15.166', 5060))  # Replace with your server IP and port if needed
            st.success("Conectado ao servidor com sucesso!")

            # Start a thread to listen for incoming messages
            st.session_state.received_messages = []
            t =  threading.Thread(target=listen_for_messages, daemon=True)
            t.start()
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

if text:
    ascii_bits = text_to_bits(text)
    st.write("Vetor ASCII de cada letra:")
    for i, char_bits in enumerate(ascii_bits):
        st.write(f"{text[i]}: {char_bits}")

    bits = ''.join(ascii_bits)
    st.session_state.bits = bits # Preserva o bit em todo codigo BITS global
    
    modulation_type = st.selectbox("Escolha o tipo de modulação", ["Digital", "Portadora"])

    if modulation_type == "Digital":
        modulation_scheme = st.selectbox(
            "Escolha a técnica de modulação digital", 
            ["NRZ-Polar", "Manchester", "Bipolar"],
            key="digital_modulation",
            on_change=set_modulation_scheme,  # Call the function to set the scheme
            args=(st.session_state.digital_modulation,)  # Pass the selected scheme
        )
    else:
        modulation_scheme = st.selectbox(
            "Escolha a técnica de modulação por portadora", 
            ["ASK", "FSK", "8-QAM"],
            key="carrier_modulation",
            on_change=set_modulation_scheme,  # Call the function to set the scheme
            args=(st.session_state.carrier_modulation,)  # Pass the selected scheme
        )

    if st.button("Modular"):
        if bits:
            bit_duration = 100  # Duration of each bit in the plot
            num_bits = len(bits)
            t = np.linspace(0, num_bits, num_bits * bit_duration)
            clock = 0.5 * (1 + np.sign(np.sin(2 * np.pi * 1 * t)))

            carrier_freq = 1
            carrier = np.sin(2 * np.pi * carrier_freq * t)

            fig, axs = plt.subplots(4, 1, figsize=(10, 10), sharex=True)

            # Expand the bits for plotting
            expanded_bits = np.repeat(list(map(int, bits)), bit_duration)
            axs[0].plot(t, expanded_bits, drawstyle='steps-pre')
            axs[0].set(title="Entrada", ylabel="Bit")
            axs[0].grid(True)
            axs[0].legend(["Entrada"])

            axs[1].plot(t, clock, drawstyle='steps-pre')
            axs[1].set(title="Clock", ylabel="Amplitude")
            axs[1].grid(True)
            axs[1].legend(["Clock"])

            if modulation_scheme == "NRZ-Polar":
                modulated_signal = np.repeat(nrz_polar(bits), bit_duration)
                #modulated_signal = nrz_polar(bits)
            elif modulation_scheme == "Manchester":
                modulated_signal = manchester(bits, clock)
            elif modulation_scheme == "Bipolar":
                modulated_signal = np.repeat(bipolar(bits), bit_duration)
            elif modulation_scheme == "ASK":
                modulated_signal = ask_modulation(nrz_polar(bits), carrier)
            elif modulation_scheme == "FSK":
                modulated_signal = fsk_modulation(nrz_polar(bits), t, carrier_freq)
            elif modulation_scheme == "8-QAM":
                modulated_signal = modulacao([int(bit) for bit in bits])
                
            # Adjust time vector to match the length of the modulated signal
            t_modulated = np.linspace(0, num_bits, len(modulated_signal))
            #if modulation_scheme in ["NRZ-Polar", "Bipolar"]:
             #   t_modulated = np.linspace(0, len(modulated_signal) / bit_duration, len(modulated_signal))
            #else:
             #   t_modulated = np.linspace(0, len(modulated_signal) / 100, len(modulated_signal))

            axs[2].plot(t_modulated, np.real(modulated_signal), drawstyle='steps-pre', label='Parte Real')
            if modulation_scheme=="8-QAM":
                axs[2].plot(t_modulated, np.imag(modulated_signal), drawstyle='steps-pre', linestyle='--', label='Parte Imaginária')
            axs[2].set(title=f"Modulado - {modulation_scheme}", ylabel="Amplitude")
            axs[2].grid(True)
            axs[2].legend([f"Modulado - {modulation_scheme}"])

            # Plot the carrier signal
            axs[3].plot(t, carrier)
            axs[3].set(title="Carrier Signal", ylabel="Amplitude")
            axs[3].grid(True)
            axs[3].legend(["Carrier"])

            st.pyplot(fig)

            try:
                if modulation_scheme == "8-QAM":
                    modulated_signal_string = signal_to_string(np.real(modulated_signal))
                    #signal_to_string(np.imag(modulated_signal))
                else:
                    modulated_signal_string = signal_to_string(modulated_signal)

                st.session_state.client_socket.send(modulated_signal_string.encode('ascii'))
                st.success(f"[{nickname}] Sinal modulado e enviado: {modulation_scheme}")

                demodula = nrz_polar_demodulation(modulated_signal)
                print(f'Demodulado : {demodula}')
                #st.session_state.client_socket.send(modulated_signal_string.encode('ascii'))
                #st.success(f"[{nickname}] Sinal modulado e enviado: {modulation_scheme}")
            except Exception as e:
                st.error(f"Erro ao enviar o sinal modulado para o servidor: {e}")

# Display received messages
st.subheader("Mensagens Recebidas")
if 'received_messages' in st.session_state:
    for message in st.session_state.received_messages:
        st.write(message)
