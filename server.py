import socket
import threading

PORT = 5060
SERVER = socket.gethostbyname(socket.gethostname())  # Local host
ADDR = (SERVER, PORT)
FORMAT = 'ascii'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            print(f"Error sending message to client: {client}")
            remove_client(client)

def handle_client(client):
    try:
        # Receive nickname
        nickname = client.recv(1024).decode(FORMAT)
        if not nickname:
            raise Exception("Failed to receive nickname")
        nicknames.append(nickname)
        clients.append(client)
        print(f"[NEW CONNECTION] {client.getpeername()} connected.")
        print(f"Nickname is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode(FORMAT))

        # Send acknowledgment
        client.send("Connected to the server!".encode(FORMAT))

        while True:
            try:
                # Receive and process the signal
                message = client.recv(1024).decode(FORMAT)
                if message:
                    signal = list(map(int, message.split(',')))  # Convert back to list of integers
                    print(f"Signal received: {signal}")
                    # Further processing...
                else:
                    break
            except Exception as e:
                print(f"Error handling client: {e}")
                break
    finally:
        remove_client(client)


def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames[index]
        broadcast(f"{nickname} left the chat!".encode(FORMAT))
        nicknames.remove(nickname)
        print(f"[DISCONNECTED] {nickname} disconnected.")

def start():
    print(f"[STARTING] Server is starting on {SERVER}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"[NEW CONNECTION] {address} connected.")
        
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start()