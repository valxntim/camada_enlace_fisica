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

# Function to broadcast messages to all connected clients
def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            print(f"Error sending message to client: {client}")
            remove_client(client)

# Function to handle individual client connections
def handle_client(client):
    try:
        # Receive and store the nickname
        nickname = client.recv(1024).decode(FORMAT)
        if not nickname:
            raise Exception("Failed to receive nickname")
        
        nicknames.append(nickname)
        clients.append(client)
        
        print(f"[NEW CONNECTION] {client.getpeername()} connected as {nickname}.")
        broadcast(f"{nickname} joined the chat!".encode(FORMAT))

        # Acknowledge connection
        client.send("Connected to the server!".encode(FORMAT))

        while True:
            try:
                # Receive and process the signal message
                message = client.recv(1024).decode(FORMAT)
                if message:
                    # Convert the signal back to a list of integers
                    signal = list(map(int, message.split(',')))
                    print(f"[{nickname}] Signal received: {signal}")
                    
                    # Broadcast the signal message to all clients
                    broadcast(f"[{nickname}] Signal received: {signal}".encode(FORMAT))
                else:
                    break
            except Exception as e:
                print(f"Error handling message from {nickname}: {e}")
                break
    finally:
        remove_client(client)

# Function to remove a client from the list and close the connection
def remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        
        nickname = nicknames[index]
        broadcast(f"{nickname} left the chat!".encode(FORMAT))
        nicknames.remove(nickname)
        print(f"[DISCONNECTED] {nickname} disconnected.")

# Function to start the server and accept new connections
def start():
    print(f"[STARTING] Server is starting on {SERVER}:{PORT}...")
    while True:
        client, address = server.accept()
        print(f"[NEW CONNECTION] {address} connected.")
        
        # Start a new thread to handle the client's connection
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start()
