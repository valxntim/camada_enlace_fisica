

import zlib

def CRC32(mensagem):
    # Calcula o CRC32 da mensagem
    crc32 = zlib.crc32(mensagem.encode())
    
    # Adiciona o CRC32 ao final da mensagem
    mensagem_com_crc = f"{mensagem}{crc32:08x}"
    
    return mensagem_com_crc
def verifica_CRC32 (mensagem_com_crc):
    # Separa a mensagem e o CRC32 da mensagem recebida
    mensagem_separada = mensagem_com_crc[:-8]
    crc32_reduzido = mensagem_com_crc[-8:]
    
    # Calcula o CRC32 da mensagem (sem o valor de CRC32)
    crc32_calculado = zlib.crc32(mensagem_separada.encode())
    
    # Converte o CRC32 calculado para hexadecimal e compara com o CRC32 recebido
    crc32_calculado_hex = f"{crc32_calculado:08x}"
    
    # Verifica se o CRC32 calculado coincide com o CRC32 recebido
    if crc32_calculado_hex == crc32_reduzido:
        return 'mensagem sem erro' # Mensagem está correta
    else:
        return 'mensagem com erro'  # Mensagem está corrompida
mensagem= input()
print(CRC32(mensagem))

