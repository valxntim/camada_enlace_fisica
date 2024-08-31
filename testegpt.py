import numpy as np

def contar_caracteres(data):
    return len(data)

def inserir_bytes(data, byte_insert):
    inserted_data = []
    for byte in data:
        inserted_data.append(byte)
        if byte == byte_insert:
            inserted_data.append(byte_insert)
    return inserted_data

def bit_paridade_par(data):
    paridade = sum(data) % 2
    return paridade == 0

def crc32(data):
    import zlib
    return zlib.crc32(data) == 0



# Test
data = [0, 1, 1, 0, 1]
byte_insert = 0x7E

# Contagem de caracteres
print("Número de caracteres:", contar_caracteres(data))

# Inserção de bytes
print("Dados após inserção de bytes:", inserir_bytes(data, byte_insert))

# Paridade par
print("Paridade par:", bit_paridade_par(data))

# CRC-32
data_bytes = b"Hello World"
print("CRC-32 correto:", crc32(data_bytes))
