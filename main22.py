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

# Convert the signal to a string
def signal_to_string(signal):
    return ','.join(map(str, signal))

# Convert the signal to bytes
def signal_to_bytes(signal):
    return bytes(signal)

# Function to store modulation scheme
def set_modulation_scheme(selected_scheme):
    st.session_state.modulation_scheme = selected_scheme

# Function to convert text to ASCII bits
def text_to_bits(text):
    return [format(ord(char), '08b') for char in text]

# NRZ-Polar modulation function
def nrz_polar(bits):
    return [1 if bit == '1' else -1 for bit in bits]

# Manchester modulation function
def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)
    nrz_expanded = np.repeat(nrz_signal, 100)
    manchester_signal = np.logical_xor(nrz_expanded > 0, clock > 0.5).astype(int)
    return manchester_signal * 2 - 1

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
    nrz_expanded = np.repeat(nrz_signal, 100)
    return np.where(nrz_expanded == 1, carrier, 0)

# FSK modulation function
def fsk_modulation(nrz_signal, t, carrier_freq):
    nrz_expanded = np.repeat(nrz_signal, 100)
    freq_high = carrier_freq * 2
    freq_low = carrier_freq
    return np.where(nrz_expanded == 1, np.sin(2 * np.pi * freq_high * t), np.sin(2 * np.pi * freq_low * t))

def downsample(signal, factor):
    return signal[::factor]



# Function to listen for incoming messages from the server
def listen_for_messages():
    while True:
        try:
            message = st.session_state.client_socket.recv(1024).decode('ascii')
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
            threading.Thread(target=listen_for_messages, daemon=True).start()
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
    st.session_state.bits = bits
    
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
            ["ASK", "FSK"],
            key="carrier_modulation",
            on_change=set_modulation_scheme,  # Call the function to set the scheme
            args=(st.session_state.carrier_modulation,)  # Pass the selected scheme
        )

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
                    # Generate and expand signal
                    signal = nrz_polar(bits)
                    signal_expanded = np.repeat(signal, 100)

                    # Plot the signal
                    axs[2].plot(t, signal_expanded, drawstyle='steps-pre')
                    axs[2].set(title="NRZ-Polar Modulation", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["NRZ-Polar"])

                    # Convert signal to string or bytes for sending
                    signal_str = signal_to_string(signal)
                    st.write(f"signal_str: {signal_str}")
                    # Ensure client socket is connected before sending
                    if st.session_state.client_socket:
                        try:
                            st.session_state.client_socket.send(signal_str.encode('ascii'))
                            st.success("Mensagem enviada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao enviar a mensagem para o servidor: {e}")

                    # Display debugging info
                    st.write(f"Bits: {bits}")
                    st.write(f"Selected Modulation Scheme: {modulation_scheme}")
                    st.write(f"Signal: {signal}")

                elif modulation_scheme == "Manchester":
                    manchester_signal = manchester(bits, clock)

                    manchester_signall = manchester_signal[1:]  # Removes the first item
                    # Example: Downsample the signal by a factor of 100
                    downsampled_signal = downsample(manchester_signall, 100)
                    axs[2].plot(t, manchester_signal, drawstyle='steps-pre')
                    axs[2].set(title="Manchester Encoding", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["Manchester"])

                    # Convert signal to string or bytes for sending
                    signal_str = signal_to_string(downsampled_signal)
                    st.write(f"signal_str: {signal_str}")
                    # Ensure client socket is connected before sending
                    if st.session_state.client_socket:
                        try:
                            st.session_state.client_socket.send(signal_str.encode('ascii'))
                            st.success("Mensagem enviada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao enviar a mensagem para o servidor: {e}")

                    # Display debugging info
                    st.write(f"Bits: {bits}")
                    st.write(f"Selected Modulation Scheme: {modulation_scheme}")
                    st.write(f"Signal: {manchester_signal}")

                elif modulation_scheme == "Bipolar":
                    signal_bipolar = bipolar(bits)
                    signal_expanded_bipolar = np.repeat(signal_bipolar, 100)
                    axs[2].plot(t, signal_expanded_bipolar, drawstyle='steps-pre')
                    axs[2].set(title="Bipolar Modulation", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["Bipolar"])

                    # Convert signal to string or bytes for sending
                    signal_str = signal_to_string(signal_bipolar)
                    st.write(f"signal_str: {signal_str}")
                    # Ensure client socket is connected before sending
                    if st.session_state.client_socket:
                        try:
                            st.session_state.client_socket.send(signal_str.encode('ascii'))
                            st.success("Mensagem enviada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao enviar a mensagem para o servidor: {e}")

                    # Display debugging info
                    st.write(f"Bits: {bits}")
                    st.write(f"Selected Modulation Scheme: {modulation_scheme}")
                    st.write(f"Signal: {signal_bipolar}")

            elif modulation_type == "Portadora":
                if modulation_scheme == "ASK":
                    nrz_signal = nrz_polar(bits)
                    signal_ask = ask_modulation(nrz_signal, carrier)
                    axs[2].plot(t, signal_ask, drawstyle='steps-pre')
                    axs[2].set(title="ASK Modulation", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["ASK"])

                    # Display debugging info
                    st.write(f"Bits: {bits}")
                    st.write(f"Selected Modulation Scheme: {modulation_scheme}")
                    st.write(f"Signal: {signal_ask}")

                elif modulation_scheme == "FSK":
                    nrz_signal = nrz_polar(bits)
                    signal_fsk = fsk_modulation(nrz_signal, t, carrier_freq)
                    axs[2].plot(t, signal_fsk, drawstyle='steps-pre')
                    axs[2].set(title="FSK Modulation", xlabel="Tempo", ylabel="Amplitude")
                    axs[2].legend(["FSK"])

                    # Display debugging info
                    st.write(f"Bits: {bits}")
                    #st.write(f"Selected Modulation Scheme: {modulation_scheme}")
                    st.write(f"Signal: {signal_fsk}")

            axs[2].grid(True)
            st.pyplot(fig)
        else:
            st.warning("Por favor, insira um texto.")
