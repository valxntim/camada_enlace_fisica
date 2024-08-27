import socket
import threading

# https://www.youtube.com/watch?v=3UOyky9sEQY&list=PL7yh-TELLS1FwBSNR_tH7qVbNpYHL4IQs

nickname = input("Escolha um Nickname: ")
PORT  = 5060
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'ascii'
user =  socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o Socket e define o tipo de conexão nesse caso IPV4
user.connect(ADDR) # conecta ao servidor

def iniciar():
  while True:
        try:
            msg = user.recv(1024).decode(FORMAT) # recebe a mensagem do cliente
            if msg == "NICK":
                user.send(nickname.encode(FORMAT))
            else:
                print(msg)
        except:
            print("Ocorreu um erro!")
            user.close()
            break
    
def escrever():
    while True:
        msg = f'{nickname}: {input("")}'
        user.send(msg.encode(FORMAT))

recebendo_thread = threading.Thread(target=iniciar)
recebendo_thread.start()

escrever_thread = threading.Thread(target=escrever)
escrever_thread.start()
