import socket
import threading

PORT  = 5060
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'ascii'
DISCONNECT_MESSAGE = "!DISCONNECT"

#print(SERVER)
server=  socket.socket(socket.AF_INET, socket.SOCK_STREAM) # cria o Socket e define o tipo de conexão nesse caso IPV4
server.bind(ADDR) # associa o socket a uma porta
server.listen() # aguarda conexões
clients = []
nicknames = []

def transmicao(mensagem):
    for client in clients:
        client.send(mensagem)

def tratando_cliente(user):
    print(f"[NOVO USUÁRIO] {user} conectada.")
    while True:
        try:
            msg = user.recv(1024).decode(FORMAT) # recebe a mensagem do cliente
            transmicao(msg)
        except:
            index = clients.index(user)
            clients.remove(user)
            user.close()
            nickname = nicknames[index]
            transmicao(f"{nickname} saiu do chat!".encode(FORMAT))
            nicknames.remove(nickname)
            break


def iniciar():
    while True:
        user, endereco = server.accept() # aguarda conexões
        print(f"[NOVA CONEXÃO] {endereco} conectada.")
        user.send("NICK".encode(FORMAT))
        nickname = user.recv(1024).decode(FORMAT)
        nicknames.append(nickname)
        clients.append(user)
        print(f'Nickname é: {nickname}')
        transmicao(f"{nickname} entrou no chat!".encode(FORMAT))
        user.send("Conectado ao servidor!".encode(FORMAT))

        thread = threading.Thread(target=tratando_cliente, args=(user,)) #Quando a user é realizada cria uma thread para tratar a conexão entrand na função tratando_cliente e passando o endereço do cliente
        thread.start()
        print(f"[CONEXÕES ATIVAS] {threading.active_count() - 1}")

print("[INICIANDO] Servidor está iniciando...")
iniciar()