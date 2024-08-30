import streamlit as st
import zlib

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
    # Pad binary string to be multiple of 8 bits
    padded_binary_str = binary_str.zfill(((len(binary_str) + 7) // 8) * 8)
    byte_list = [padded_binary_str[i:i+8] for i in range(0, len(padded_binary_str), 8)]
    return bytes([int(b, 2) for b in byte_list])

def bytes_to_bin(byte_data):
    return ''.join(format(byte, '08b') for byte in byte_data)

def calculate_crc32(data):
    """Calcula o CRC-32 dos dados."""
    return zlib.crc32(data) & 0xFFFFFFFF

def add_crc32(data):
    """Adiciona o CRC-32 aos dados."""
    crc = calculate_crc32(data)
    return data + crc.to_bytes(4, byteorder='big')

def verify_crc32(data_with_crc):
    """Verifica o CRC-32 dos dados."""
    data = data_with_crc[:-4]
    expected_crc = int.from_bytes(data_with_crc[-4:], byteorder='big')
    return calculate_crc32(data) == expected_crc

def calculate_parity_bit(byte):
    """Calcula o bit de paridade par para um byte."""
    return '0' if bin(byte).count('1') % 2 == 0 else '1'

def add_parity_bits(data):
    """Adiciona o bit de paridade par a cada byte no dado."""
    data_with_parity = ""
    for byte in data:
        # Adiciona o byte e o bit de paridade
        data_with_parity += format(byte, '08b') + calculate_parity_bit(byte)
    return data_with_parity

def verify_parity_bits(data_with_parity):
    """Verifica a integridade dos bits de paridade."""
    for i in range(0, len(data_with_parity), 9):  # 8 bits de dados + 1 bit de paridade
        byte = data_with_parity[i:i+8]
        parity_bit = data_with_parity[i+8]
        if parity_bit != calculate_parity_bit(int(byte, 2)):
            return False
    return True

def hamming_encode(data):
    """Codifica os dados usando o código de Hamming (7,4)."""
    encoded_data = ""
    for byte in data:
        bits = format(byte, '08b')
        d = [int(bit) for bit in bits]
        p1 = d[0] ^ d[1] ^ d[3] ^ d[4] ^ d[6]
        p2 = d[0] ^ d[2] ^ d[3] ^ d[5] ^ d[6]
        p4 = d[1] ^ d[2] ^ d[3]
        p8 = d[4] ^ d[5] ^ d[6] ^ d[7]
        encoded_bits = [p1, p2, d[0], p4, d[1], d[2], d[3], p8, d[4], d[5], d[6], d[7]]
        encoded_data += ''.join(map(str, encoded_bits))
    return encoded_data

def hamming_decode(encoded_bits):
    """Decodifica os dados usando o código de Hamming (7,4)."""
    decoded_data = ""
    for i in range(0, len(encoded_bits), 12):
        bits = encoded_bits[i:i+12]
        b = [int(bit) for bit in bits]
        p1 = b[0]
        p2 = b[1]
        p4 = b[3]
        p8 = b[7]
        d = b[2:4] + b[5:7] + b[8:12]
        s1 = p1 ^ b[2] ^ b[4] ^ b[6] ^ b[8]
        s2 = p2 ^ b[2] ^ b[5] ^ b[6] ^ b[9]
        s4 = p4 ^ b[4] ^ b[5] ^ b[6] ^ b[10]
        s8 = p8 ^ b[8] ^ b[9] ^ b[10] ^ b[11]
        error_position = s1 * 1 + s2 * 2 + s4 * 4 + s8 * 8
        if error_position != 0:
            print(f"Error detected at position {error_position}")
            b[error_position - 1] ^= 1  # Corrige o erro
        decoded_data += ''.join(map(str, b[2:4] + b[5:7] + b[8:12]))
    return decoded_data

# Streamlit UI
st.title('Byte Processing Tool')

# Entrada de texto para os bytes (em binário)
byte_input = st.text_input("Enter bytes (binary, e.g., 01001000011001010110110001101100)")

# Escolha do método de codificação
method = st.selectbox("Choose a method", ["Inserção de Bytes", "Contagem de Caracteres", "Paridade", "CRC-32", "Hamming"])

if st.button("Process"):
    try:
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
        elif method == "Paridade":
            data_bytes = bin_to_bytes(byte_input)
            data_with_parity = add_parity_bits(data_bytes)
            st.write("Data with Parity Bits (binary):", data_with_parity)
            is_valid = verify_parity_bits(data_with_parity)
            st.write("Parity Check Result:", "Valid" if is_valid else "Invalid")
            print("Data with Parity Bits (binary):", data_with_parity)
            print("Parity Check Result:", "Valid" if is_valid else "Invalid")
        elif method == "CRC-32":
            data_bytes = bin_to_bytes(byte_input)
            data_with_crc = add_crc32(data_bytes)
            st.write("Data with CRC-32 (binary):", bytes_to_bin(data_with_crc))
            is_valid = verify_crc32(data_with_crc)
            st.write("CRC Check Result:", "Valid" if is_valid else "Invalid")
            print("Data with CRC-32 (binary):", bytes_to_bin(data_with_crc))
            print("CRC Check Result:", "Valid" if is_valid else "Invalid")
        elif method == "Hamming":
            data_bytes = bin_to_bytes(byte_input)
            encoded_data = hamming_encode(data_bytes)
            st.write("Encoded Data with Hamming (binary):", encoded_data)
            
            decoded_data_bin = hamming_decode(encoded_data)
            decoded_data = bin_to_bytes(decoded_data_bin)
            
            # Convert original data to binary string for comparison
            original_data_bin = ''.join(format(byte, '08b') for byte in data_bytes)
            decoded_data_bin_str = ''.join(format(byte, '08b') for byte in decoded_data)
            
            st.write("Decoded Data (binary):", decoded_data_bin_str)
            st.write("Hamming Check Result:", "Valid" if original_data_bin == decoded_data_bin_str else "Invalid")
            print("Encoded Data with Hamming (binary):", encoded_data)
            print("Decoded Data (binary):", decoded_data_bin_str)
            print("Hamming Check Result:", "Valid" if original_data_bin == decoded_data_bin_str else "Invalid")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")