import numpy as np

def calcular_paridade_bits(dado):
    """Calcula os bits de paridade para o código Hamming (7,4)."""
    data = np.array([int(bit) for bit in dado], dtype=int)
    paridade = np.zeros(3, dtype=int)
    
    # Bits de paridade (posição 1, 2 e 4) para 4 dados
    paridade[0] = (data[0] + data[1] + data[3]) % 2
    paridade[1] = (data[0] + data[2] + data[3]) % 2
    paridade[2] = (data[1] + data[2] + data[3]) % 2
    
    return paridade

def adicionar_codigo_hamming(dado):
    """Adiciona código Hamming (7,4) aos dados."""
    if len(dado) != 4:
        raise ValueError("O dado deve ter exatamente 4 bits.")
    
    paridade = calcular_paridade_bits(dado)
    return ''.join(dado[i] for i in [0, 1, 2, 3]) + ''.join(map(str, paridade))

def verificar_erro_hamming(codigo):
    """Verifica e corrige erros usando código Hamming (7,4)."""
    data = np.array([int(bit) for bit in codigo], dtype=int)
    p1 = (data[0] + data[1] + data[3] + data[4] + data[6]) % 2
    p2 = (data[0] + data[2] + data[3] + data[5] + data[6]) % 2
    p4 = (data[1] + data[2] + data[3] + data[6]) % 2
    
    erro = p1 * 1 + p2 * 2 + p4 * 4
    if erro != 0:
        print(f"Erro detectado na posição: {erro}")
        # Corrigir erro
        codigo = list(codigo)
        codigo[erro - 1] = '1' if codigo[erro - 1] == '0' else '0'
        codigo = ''.join(codigo)
        print(f"Codigo corrigido: {codigo}")
    
    return codigo

def extrair_dado(codigo_corrigido):
    """Extrai o dado de 4 bits do código Hamming corrigido."""
    return codigo_corrigido[0:4]


def pacote_completo(dado):
    """Integra contagem de caracteres, byte stuffing e código Hamming."""
    dado_com_contagem = adicionar_contagem_de_caracteres(dado)
    dado_com_stuffing = adicionar_byte_stuffing(dado_com_contagem.encode())
    
    # Converter dados para binário e aplicar código Hamming
    dados_binarios = ''.join(format(byte, '08b') for byte in dado_com_stuffing)
    dados_hamming = [adicionar_codigo_hamming(dados_binarios[i:i+4]) for i in range(0, len(dados_binarios), 4)]
    pacote_final = ''.join(dados_hamming)
    
    # Adicionar bit de paridade (opcional)
    bit_paridade = calcular_bit_paridade(pacote_final.encode())
    pacote_final = pacote_final + str(bit_paridade)
    
    return pacote_final

def receber_pacote(pacote):
    """Recebe o pacote e realiza a verificação de integridade usando Hamming."""
    try:
        # Remover o bit de paridade (opcional)
        bit_paridade_enviado = pacote[-1]
        pacote_sem_paridade = pacote[:-1]
        
        # Verificar e corrigir erros de Hamming
        dados_hamming_corrigidos = []
        for i in range(0, len(pacote_sem_paridade), 7):
            codigo_hamming = pacote_sem_paridade[i:i+7]
            codigo_corrigido = verificar_erro_hamming(codigo_hamming)
            dados_hamming_corrigidos.append(codigo_corrigido)
        
        dados_binarios_corrigidos = ''.join(dados_hamming_corrigidos)
        
        # Remover byte stuffing
        dado_com_stuffing = bytes(int(dados_binarios_corrigidos[i:i+8], 2) for i in range(0, len(dados_binarios_corrigidos), 8))
        dado_com_contagem = remover_byte_stuffing(dado_com_stuffing)
        
        dado = remover_contagem_de_caracteres(dado_com_contagem.decode())
        print(f"Dado recebido: {dado}")
    except ValueError as e:
        print(f"Erro na recepção: {e}")


# Exemplo de uso
dado = "Mensagem de exemplo"
pacote = pacote_completo(dado)
print(f"Pacote enviado: {pacote}")

receber_pacote(pacote)

# Exemplo de uso
dado = "1101"  # 4 bits de dados
codigo_hamming = adicionar_codigo_hamming(dado)
print(f"Código Hamming gerado: {codigo_hamming}")

# Simular erro: inverte o terceiro bit
codigo_hamming_com_erro = codigo_hamming[:2] + ('0' if codigo_hamming[2] == '1' else '1') + codigo_hamming[3:]
print(f"Código Hamming com erro: {codigo_hamming_com_erro}")

codigo_corrigido = verificar_erro_hamming(codigo_hamming_com_erro)
dado_corrigido = extrair_dado(codigo_corrigido)
print(f"Dado corrigido: {dado_corrigido}")
