import socket
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import threading
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from camadafisica import *


# Initialize session state variables
if 'digital_modulation' not in st.session_state:
    st.session_state.digital_modulation = None

if 'fig' not in st.session_state:
    st.session_state.fig = None

if 'carrier_modulation' not in st.session_state:
    st.session_state.carrier_modulation = None

if 'modulation_scheme' not in st.session_state:
    st.session_state.modulation_scheme = None

if 'bits' not in st.session_state:
    st.session_state.bits = None

if 'client_socket' not in st.session_state:
    st.session_state.client_socket = None

# Function to store modulation scheme
def set_modulation_scheme(selected_scheme):
    st.session_state.modulation_scheme = selected_scheme

# Function to listen for incoming messages from the server
#@st.experimental_fragment 
def listen_for_messages():
    while True:
        try:
            #print(clientsocket)
            message = st.session_state.client_socket.recv(1048576).decode('ascii')
            if message:
                st.session_state.received_messages.append(message)
                #sleep(5)
                st.rerun()
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
            t = threading.Thread(target=listen_for_messages, daemon=True)
            add_script_run_ctx(t)
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
    st.session_state.bits = bits  # Preserva o bit em todo código

    modulation_type = st.selectbox("Escolha o tipo de modulação", ["Digital", "Portadora"])

    if modulation_type == "Digital":
        modulation_scheme = st.selectbox(
            "Escolha a técnica de modulação digital", 
            ["NRZ-Polar", "Manchester", "Bipolar"],
            key="digital_modulation",
            on_change=set_modulation_scheme,
            args=(st.session_state.digital_modulation,)
        )
    else:
        modulation_scheme = st.selectbox(
            "Escolha a técnica de modulação por portadora", 
            ["ASK", "FSK", "8-QAM"],
            key="carrier_modulation",
            on_change=set_modulation_scheme,
            args=(st.session_state.carrier_modulation,)
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
            elif modulation_scheme == "Manchester":
                modulated_signal = manchester(bits, clock)
                #print(modulated_signal)
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

            axs[2].plot(t_modulated, np.real(modulated_signal), drawstyle='steps-pre', label='Parte Real')
            if modulation_scheme == "8-QAM":
                axs[2].plot(t_modulated, np.imag(modulated_signal), drawstyle='steps-pre', linestyle='--', label='Parte Imaginária')
            axs[2].set(title=f"Modulado - {modulation_scheme}", ylabel="Amplitude")
            axs[2].grid(True)
            axs[2].legend([f"Modulado - {modulation_scheme}"])

            # Plot the carrier signal
            axs[3].plot(t, carrier)
            axs[3].set(title="Carrier Signal", ylabel="Amplitude")
            axs[3].grid(True)
            axs[3].legend(["Carrier"])

            st.session_state.fig = fig
            
            st.pyplot(fig)
            #sleep(5)
            signal_reduzido = []
            if modulation_scheme == "Manchester":
                for i in range(1,len(modulated_signal),50):
                    signal_reduzido.append(modulated_signal[i])
            else:
                for i in range(0,len(modulated_signal),100):
                    signal_reduzido.append(modulated_signal[i])
            #print(signal_reduzido)
            try:
                if modulation_scheme == "8-QAM":
                    modulated_signal_string = signal_to_string(np.real(signal_reduzido))
                else:
                    modulated_signal_string = signal_to_string(signal_reduzido)
                #st.session_state.client_socket.send(signal_to_string(signal_reduzido).encode('ascii'))
                st.session_state.client_socket.send(modulated_signal_string.encode('ascii'))
                st.success(f"[{nickname}] Sinal modulado e enviado como: {modulation_scheme}")

                #demodula = bits_to_ascii(nrz_polar_demodulation(signal_reduzido))
                #print(f'Demodulado : {demodula}')
                #st.rerun()
            except Exception as e:
                st.error(f"Erro ao enviar o sinal modulado para o servidor: {e}")

# Display received messages
st.subheader("Mensagens Recebidas")
if 'received_messages' in st.session_state:
    for message in st.session_state.received_messages:
        st.write(message)