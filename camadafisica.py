import numpy as np

# NRZ-Polar modulation function
def nrz_polar_demodulation(bits):
    return [0 if int(bit) == -1 else  1 for bit in bits]

def bits_to_ascii(bit_list):
    # Converte a lista de bits para uma string
    bit_string = ''.join(str(bit) for bit in bit_list)
    
    # Converte a string de bits para um número decimal
    decimal_value = int(bit_string, 2)
    
    # Converte o valor decimal para o caractere ASCII correspondente
    ascii_char = chr(decimal_value)
    
    return ascii_char

# Function to convert text to ASCII bits
def text_to_bits(text):
    return [format(ord(char), '08b') for char in text]

# NRZ-Polar modulation function
def nrz_polar(bits):
    return [1 if bit == '1' else -1 for bit in bits]

# Manchester modulation function with expanded clock
def manchester(bits, clock):
    nrz_signal = nrz_polar(bits)
    nrz_expanded = np.repeat(nrz_signal, len(clock) // len(nrz_signal))
    manchester_signal = np.logical_xor(nrz_expanded > 0, clock > 0.5).astype(int)
    return manchester_signal * 2 - 1  # Convert Binary to Bipolar

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
    nrz_expanded = np.repeat(nrz_signal, len(carrier) // len(nrz_signal))
    return np.where(nrz_expanded == 1, carrier, 0)

# FSK modulation function
def fsk_modulation(nrz_signal, t, carrier_freq):
    nrz_expanded = np.repeat(nrz_signal, len(t) // len(nrz_signal))
    freq_high = carrier_freq * 2
    freq_low = carrier_freq
    return np.where(nrz_expanded == 1, np.sin(2 * np.pi * freq_high * t[:len(nrz_expanded)]), 
                               np.sin(2 * np.pi * freq_low * t[:len(nrz_expanded)]))

# 8-QAM modulation function
def modulacao(bits):
    constelacao = {
            (0, 0, 0): complex(-1, -1), #0
            (0, 0, 1): complex(-1, 1),  #1  
            (0, 1, 0): complex(1, -1),  #2
            (0, 1, 1): complex(1, 1),   #3
            (1, 0, 0): complex(-1, -3), #4
            (1, 0, 1): complex(-1, 3),  #5
            (1, 1, 0): complex(1, -3),  #6
            (1, 1, 1): complex(1, 3)    #7
            }

    tam = len(bits) 

    if tam % 3 != 0:
        while tam % 3 != 0:
            bits.append(0)
            tam = len(bits)

    # Converte bits em símbolos 8QAM 
    bits_simbolos = []
    for i in range(0, len(bits), 3):
        # Cria uma tupla manualmente de 3 em 3 bits
        simbolo = (bits[i], bits[i+1] if i+1 < len(bits) else 0, bits[i+2] if i+2 < len(bits) else 0)
        bits_simbolos.append(simbolo)

    # Inicializa uma lista vazia para armazenar os símbolos modulados
    simbolos_modulados = []
    for simbolo in bits_simbolos:
        # Adiciona cada símbolo mapeado à lista manualmente
        simbolos_modulados.append(constelacao[simbolo])

    # Retorna a lista de símbolos modulados
    return banda_base_8qam(simbolos_modulados)

def banda_base_8qam(simbolos_modulados):
    duracao_simbolo = 3  # Duração de cada símbolo
    num_simbolos = len(simbolos_modulados)
    
    # Vetor de tempo para um símbolo
    tempo_simbolo = np.linspace(0, duracao_simbolo, 100)
    
    # Vetor de tempo total
    tempo_total = np.linspace(0, duracao_simbolo * num_simbolos, num_simbolos * 100)

    # Inicializa a forma de onda como um array de zeros, com tipo complexo para suportar parte real e imaginária
    forma_onda = np.zeros(len(tempo_total), dtype=complex)

    for i in range(num_simbolos):
        inicio = i * 100
        fim = (i + 1) * 100
        
        # Obter o símbolo atual
        simbolo = simbolos_modulados[i]
        
        # Modula o sinal e armazena na forma de onda (usando a função exponencial complexa)
        forma_onda[inicio:fim] = simbolo * np.exp(1j * 2 * np.pi * 1 * tempo_simbolo)

    #print(forma_onda)
    return forma_onda

# Function to convert a modulated signal back to a string
def signal_to_string(signal):
    return ','.join(str(bit) for bit in signal)
