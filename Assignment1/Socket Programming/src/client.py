import threading
from socket import *



serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)

try:
    clientSocket.connect((serverName,serverPort))
except Exception as e:
    print(f"Unable to connect to server: {e}")
    exit()

try: # prevents error when server closed connection while client was waiting for name, such as if the server rejected it, it crashed, or the server closed the socket before client handled handshake
    name_msg = clientSocket.recv(1024).decode() # acknowledge that we recieved a name

except ConnectionResetError:
    print("Server closed the connection.")
    clientSocket.close()
    exit()
# detect if server is full
if name_msg == "SERVER_FULL":
    print("Server is full! Connection has been rejected.")
    clientSocket.close()
    exit()


if name_msg.startswith("NAME:"):
    client_name = name_msg[5:].strip() # strip whitespace from client name
    print(f"Assigned name: {client_name}")

    # send the name to the server
    clientSocket.send(client_name.encode())

def receive_messages(sock): #recieve messages loop
  while True:
    try:
        message = sock.recv(1024) # can receive messages up to 1024 bytes
        if not message:
            print("\nServer disconnected.")
            break
        #decode incoming bytes
        decoded = message.decode()
        print(f"\nServer: {decoded}")
        
    except Exception as e:
        print(f"Receive error: {e}")
        break   






receiveThread = threading.Thread( # this runs at the same time as the while loop which ensures that we can recieve messages while waiting to send messages.
    target=receive_messages, args=(clientSocket, daemon=False)
)

receiveThread.start()

print("Connected to chat/file server.")
print("Commands: 'status', 'list', 'get <filename>', 'exit', or any text for ACK.")

# main command prompt loop

while True: # wwaiting for user input
    sentence = input("Enter command/message: ")
    if not sentence.strip():
        continue
    # send input to server
    try:
        clientSocket.send(sentence.encode())

    except Exception as e:
        print(f"Send error: {e}")
        break
    
    # user typed exit
    if sentence.lower() == 'exit':
        print("Disconnecting from server...")
        break



clientSocket.close()
receiveThread.join(timeout=1) # allows thread to finish before python quits