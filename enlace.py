import streamlit as st

# Entrada - 011011111111111111110010
# saida msg 011011111111111111110010
# Resultado - 01111110 011011111011111011111010010 01111110
# Oque o sit- 01111110 011011111011111011111010010 01111110

def byte_stuffing(bits):
    FLAG = "01111110"
    stuffed_bits = ""
    consecutive_ones = 0

    for bit in bits:
        stuffed_bits += bit  # Adiciona o bit atual
        if bit == '1':
            consecutive_ones += 1
            if consecutive_ones == 5:
                stuffed_bits += '0'  # Insere o bit 0 após cinco 1s consecutivos
                consecutive_ones = 0
        else:
            consecutive_ones = 0

    # Adiciona as FLAGS no início e no final
    return FLAG + stuffed_bits + FLAG

def byte_unstuffing(stuffed_bits):
    FLAG = "01111110"
    unstuffed_bits = ""
    consecutive_ones = 0

    # Remove as FLAGS no início e no final
    stuffed_bits = stuffed_bits[len(FLAG):-len(FLAG)]

    i = 0
    while i < len(stuffed_bits):
        bit = stuffed_bits[i]

        if consecutive_ones == 5:
            if bit == '0':
                consecutive_ones = 0
                i += 1  # Pula o bit de stuffing (o 0 inserido)
                continue

        unstuffed_bits += bit

        if bit == '1':
            consecutive_ones += 1
        else:
            consecutive_ones = 0

        i += 1

    return unstuffed_bits

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
    return ''.join(format(byte, '08b') for byte in byte_data)

# Streamlit UI
st.title('Byte Processing Tool')

# Entrada de texto para os bytes (em binário)
byte_input = st.text_input("Enter bytes (binary, e.g., 01001000011001010110110001101100)")

# Escolha do método de codificação
method = st.selectbox("Choose a method", ["Inserção de Bytes", "Contagem de Caracteres"])

if st.button("Process"):
    if method == "Inserção de Bytes":
        stuffed = byte_stuffing(byte_input)
        unstuffed = byte_unstuffing(stuffed)
        st.write("Stuffed Data (binary):", stuffed)
        st.write("Unstuffed Data (binary):", unstuffed)
        print("Stuffed Data (binary):", stuffed)
        print("Unstuffed Data (binary):", unstuffed)
    elif method == "Contagem de Caracteres":
        data_bytes = bin_to_bytes(byte_input)
        encoded_frame = character_count_encoding(data_bytes)
        decoded_data = character_count_decoding(encoded_frame)
        st.write("Encoded Frame (binary):", bytes_to_bin(encoded_frame))
        st.write("Decoded Data (binary):", bytes_to_bin(decoded_data))
        print("Encoded Frame (binary):", bytes_to_bin(encoded_frame))
        print("Decoded Data (binary):", bytes_to_bin(decoded_data))
