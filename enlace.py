import streamlit as st

def byte_stuffing(data):
    FLAG  = b'\x7E'
    stuffed_data = b''
    consecutive_ones = 0

    for byte in data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1
            stuffed_data += bytes([bit])

            if bit == 1:
                consecutive_ones += 1
                if consecutive_ones == 5:
                    stuffed_data += bytes([0])
                    consecutive_ones = 0
            else:
                consecutive_ones = 0

    return FLAG + stuffed_data + FLAG


def byte_unstuffing(stuffed_data):
    unstuffed_data = b''
    consecutive_ones = 0

    # Remove FLAGs at the start and end
    stuffed_data = stuffed_data[1:-1]

    for byte in stuffed_data:
        for i in range(8):
            bit = (byte >> (7 - i)) & 1

            if consecutive_ones == 5:
                if bit == 0:
                    consecutive_ones = 0
                    continue  # Skip this stuffed bit

            unstuffed_data += bytes([bit])

            if bit == 1:
                consecutive_ones += 1
            else:
                consecutive_ones = 0

    return unstuffed_data

def character_count_encoding(data):
    length = len(data) + 1
    return bytes([length]) + data

def character_count_decoding(frame):
    length = frame[0]
    return frame[1:length]

def bin_to_bytes(binary_str):
    byte_list = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    return bytes([int(b, 2) for b in byte_list])

def bytes_to_bin(byte_data):
    return ' - '.join(format(byte, '08b') for byte in byte_data)

# Streamlit UI
st.title('Byte Processing Tool')

# Entrada de texto para os bytes (em binário)
byte_input = st.text_input("Enter bytes (binary, e.g., 01001000011001010110110001101100)")

# Conversão de string binária para bytes
try:
    data = bin_to_bytes(byte_input)
except ValueError:
    st.error("Please enter a valid binary string.")
    st.stop()

# Escolha do método de codificação
method = st.selectbox("Choose a method", ["Inserção de Bytes", "Contagem de Caracteres"])

if st.button("Process"):
    if method == "Inserção de Bytes":
        stuffed = byte_stuffing(data)
        unstuffed = byte_unstuffing(stuffed)
        st.write("Stuffed Data (binary):", bytes_to_bin(stuffed))
        st.write("Unstuffed Data (binary):", bytes_to_bin(unstuffed))
        print("Stuffed Data (binary):", bytes_to_bin(stuffed))
        print("Unstuffed Data (binary):", bytes_to_bin(unstuffed))
    elif method == "Contagem de Caracteres":
        encoded_frame = character_count_encoding(data)
        decoded_data = character_count_decoding(encoded_frame)
        st.write("Encoded Frame (binary):", bytes_to_bin(encoded_frame))
        st.write("Decoded Data (binary):", bytes_to_bin(decoded_data))
        print("Encoded Frame (binary):", bytes_to_bin(encoded_frame))
        print("Decoded Data (binary):", bytes_to_bin(decoded_data))
