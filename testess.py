def string_para_bits(texto):
    bits = ""
    for caractere in texto:
        bits += bin(ord(caractere))[2:]  # Remove os primeiros 2 caracteres ('0b')
    return bits

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
    paridade_bit = mensagem[-1]
    for bit in mensagem:
        if bit == '1':
            count_2 += 1
    if count_2 % 2  != paridade_bit:
        print('Mensagem com erro')
    else:
        print('Mensagem correta')

mensagem = 'oi'
print(paridade_bit(mensagem))