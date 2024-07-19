import matplotlib.pyplot as plt
import streamlit as st


def nrz_polar(bits):
    signal = []
    for bit in bits:
        if bit == '0':
            signal.append(-1)
        else:
            signal.append(1)
    return signal

st.title("Modulação NRZ-Polar")

bits = st.text_input("Digite os bits (ex: 10110011):")

if st.button("Modular"):
    if bits:
        signal = nrz_polar(bits)
        
        fig, ax = plt.subplots()
        ax.plot(signal, drawstyle='steps-pre')
        ax.set(title="NRZ-Polar Modulation", xlabel="Bits", ylabel="Amplitude")
        ax.grid(True)

        st.pyplot(fig)
    else:
        st.warning("Por favor, insira uma sequência de bits.")
