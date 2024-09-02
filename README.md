# camada_enlace_fisica

Este projeto simula o funcionamento das camadas de enlace e física em redes de comunicação, abordando a implementação de protocolos de enquadramento, modulação banda-base e modulação por portadora. O objetivo é fornecer uma visão detalhada e prática desses processos por meio de um simulador desenvolvido em Python.

## Funcionalidades

- **Camada de Enlace:** Implementa protocolos de enquadramento de dados (Contagem de Caracteres e Inserção de Bytes), detecção de erros (Bit de Paridade Par e CRC) e correção de erros utilizando o Código de Hamming.
- **Camada Física:** Simula técnicas de modulação banda-base (NRZ, Manchester, Bipolar) e modulação por portadora (ASK, FSK, 8-QAM).

## Pré-requisitos

Antes de executar o projeto, é necessário instalar as dependências. O projeto inclui um arquivo `requirements.txt` que lista todas as bibliotecas necessárias.

1. **Instalar as dependências:**



   pip install -r requirements.txt


Instruções de Execução
Iniciar o Servidor:

O script server.py deve ser inicializado em um terminal separado. Ele é responsável por gerenciar as conexões dos clientes e processar as mensagens.



python server.py
Executar a Interface Streamlit:

Após iniciar o servidor, você pode rodar a interface do usuário utilizando Streamlit. Abra um segundo terminal e execute o seguinte comando:


Copy code
streamlit run interface.py
Isso iniciará a aplicação Streamlit, onde você poderá interagir com o simulador e visualizar os resultados da modulação e dos protocolos de enlace.

Como Usar
Conectar ao Servidor: Na interface Streamlit, insira um apelido e conecte-se ao servidor clicando no botão correspondente.
Enviar Mensagens: Digite o texto desejado e selecione o tipo de modulação. Clique em "Modular" para visualizar o sinal modulado e enviá-lo ao servidor.
Visualizar Resultados: As mensagens recebidas serão exibidas na interface, mostrando o sinal modulado e sua versão demodulada.
Links Úteis
Repositório GitHub
Se houver problemas ou dúvidas, sinta-se à vontade para abrir uma issue no repositório do GitHub ou contatar os membros do grupo.

Desenvolvido por:

Gustavo Almeida Valentim - Matrícula: 20/2014468
Guilherme Henrique Oliveira - Matrícula: 21/1026646
Aluizio Oliveira - Matrícula: 20/2042720
