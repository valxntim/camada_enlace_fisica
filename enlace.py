import streamlit as st
import zlib

def text_to_bits(mensagem):
    # Verifica se a mensagem é uma sequência de bits (0s e 1s) contínua
    if all(bit in '01' for bit in mensagem):
        return mensagem
    else:
        # Converte cada caractere do texto em sua representação binária de 8 bits
        bits = ''.join(format(ord(char), '08b') for char in mensagem)
        return bits


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

def bitlist_to_string(bitlist):
    return ''.join(str(bit) for bit in bitlist)

def bytes_to_bitlist(data):
    bitlist = []
    for byte in data:
        for i in range(8):
            bitlist.append((byte >> (7-i)) & 1)
    return bitlist

def bitlist_to_bytes(bitlist):
    byte_array = bytearray()
    for i in range(0, len(bitlist), 8):
        byte = 0
        for bit in bitlist[i:i+8]:
            byte = (byte << 1) | bit
        byte_array.append(byte)
    return bytes(byte_array)

def CRC32(mensagem):
    # Calcula o CRC32 da mensagem
    crc32 = zlib.crc32(mensagem.encode())
    # Adiciona o CRC32 ao final da mensagem (em hexadecimal)
    mensagem_com_crc = f"{mensagem}{crc32:08x}"
    
    return mensagem_com_crc

def verifica_CRC32(mensagem_com_crc):
    # Separa a mensagem e o CRC32 da mensagem recebida
    mensagem_separada = mensagem_com_crc[:-8]
    crc32_reduzido = mensagem_com_crc[-8:]
    
    # Calcula o CRC32 da mensagem (sem o valor de CRC32)
    crc32_calculado = zlib.crc32(mensagem_separada.encode())
    # Converte o CRC32 calculado para hexadecimal e compara com o CRC32 recebido
    crc32_calculado_hex = f"{crc32_calculado:08x}"
    
    # Verifica se o CRC32 calculado coincide com o CRC32 recebido
    if crc32_calculado_hex == crc32_reduzido:
        return 'Mensagem sem erro'  # Mensagem está correta
    else:
        return 'Mensagem com erro'  # Mensagem está corrompida

def paridade_bit(mensagem):
    count = 0
    # Conta o número de bits 1 na mensagem
    for bit in mensagem:
        if bit == '1':
            count += 1
    
    # Determina o bit de paridade
    if count % 2 ==0:
        bit_paridade = '0'
    else:
        bit_paridade = '1'
    
    # Adiciona o bit de paridade ao final da mensagem
    return mensagem + bit_paridade

def verifica_paridade(mensagem):
    x= ''
    contador= 0
    paridade_bit = mensagem[-1]
    for bit in mensagem[-1]:
        if bit == '1':
            contador += 1
    if contador % 2 == int(paridade_bit):
        x= 'Mensagem sem erro'
    else:
        x='Mensagem com erro'
    return x

def hamming_encode(data):
    print("TIPO do encode :" , type(data))
    print("DATA do encode :" ,data)
    bits = list(''.join(format(byte, '08b') for byte in data))
    tam = len(bits)
    paridade_positions = [2**i for i in range(len(bits).bit_length())]

    # Inserir bits de paridade nas posições apropriadas
    for pos in reversed(paridade_positions):
        bits.insert(pos - 1, '0')  # Inicialmente, os bits de paridade são 0

    # Calcula os valores dos bits de paridade
    for pos in paridade_positions:
        paridade = 0
        for i in range(1, len(bits) + 1):
            if i & pos:
                paridade ^= int(bits[i - 1])
        bits[pos - 1] = str(paridade)

    # Converte a lista de bits de volta para bytes
    bit_string = ''.join(bits)
    return bin_to_bytes(bit_string)

def hamming_decode(data):
    # bytes -> lista
    # lista -> string
    # string -> bits
    data = bytes_to_bitlist(data)
    print("TIPO :" , type(data))
    print("DATA :" ,data)
    bits = list(bytes_to_bin(data))
    tam = len(bits)
    paridade_positions = [2**i for i in range(len(bits).bit_length())]

    erro_posicao = 0
    for pos in paridade_positions:
        paridade = 0
        for i in range(1, len(bits) + 1):
            if i & pos:
                paridade ^= int(bits[i - 1])
        if paridade != 0:
            erro_posicao += pos

    if erro_posicao > 0:
        print(f"Erro detectado na posição {erro_posicao}. Corrigindo...")
        bits[erro_posicao - 1] = '0' if bits[erro_posicao - 1] == '1' else '1'  # Corrige o bit com erro

    # Remove os bits de paridade para recuperar a mensagem original
    mensagem_original = [bits[i - 1] for i in range(1, tam + 1) if i not in paridade_positions]
    
    # Converte a lista de bits de volta para bytes
    mensagem_original = bitlist_to_string(mensagem_original)
    print("Converteu pra string?" , type(mensagem_original))
    bit_string = ''.join(mensagem_original)
    return bin_to_bytes(bit_string)

# Streamlit UI
st.title('Byte Processing Tool')

# Entrada de texto para os bytes (em binário)
byte_input = st.text_input("Enter text")

# Escolha do método de codificação
method = st.selectbox("Choose a method", ["Inserção de Bytes", "Contagem de Caracteres", "Paridade", "CRC-32", "Hamming"])

if st.button("Process"):
    try:
        # Converte a entrada de texto em bits
        bits_input = text_to_bits(byte_input)

        if method == "Paridade":
            # Usa a função paridade_bit
            mensagem_com_paridade = paridade_bit(bits_input)
            st.write("Mensagem com bit de paridade (binário):", mensagem_com_paridade)
            resultado_verificacao = verifica_paridade(mensagem_com_paridade)
            st.write("Resultado da verificação de paridade:", resultado_verificacao)
            
        elif method == "Inserção de Bytes":
            stuffed = byte_stuffing(bits_input)
            unstuffed = byte_unstuffing(stuffed)
            st.write("Stuffed Data (binary):", stuffed)
            st.write("Unstuffed Data (binary):", unstuffed)
            
        elif method == "Contagem de Caracteres":
            data_bytes = bin_to_bytes(bits_input)
            encoded_frame = character_count_encoding(data_bytes)
            decoded_data = character_count_decoding(encoded_frame)
            st.write("Encoded Frame (binary):", bytes_to_bin(encoded_frame))
            st.write("Decoded Data (binary):", bytes_to_bin(decoded_data))
            
        elif method == "CRC-32":
            data_bytes = bin_to_bytes(bits_input)
            # Convert bytes to string for CRC calculation
            data_str = bytes_to_bin(data_bytes)
            data_with_crc = CRC32(data_str)
            st.write("Data with CRC-32 (binary):", data_with_crc)
            
            # Check CRC validity
            check_result = verifica_CRC32(data_with_crc)
            st.write("CRC Check Result:", check_result)
            
        elif method == "Hamming":
            data_bytes = bin_to_bytes(bits_input)
            encoded_data = hamming_encode(data_bytes)
            st.write("Encoded Data with Hamming (binary):", bytes_to_bin(encoded_data))
            
            decoded_data = hamming_decode(encoded_data)
            decoded_data_bin_str = ''.join(format(byte, '08b') for byte in decoded_data)
            
            # Convert original data to binary string for comparison
            original_data_bin = ''.join(format(byte, '08b') for byte in data_bytes)
            
            st.write("Decoded Data (binary):", decoded_data_bin_str)
            st.write("Hamming Check Result:", "Valid" if original_data_bin == decoded_data_bin_str else "Invalid")
                       
    except Exception as e:
        st.error(f"An error occurred: {e}")
