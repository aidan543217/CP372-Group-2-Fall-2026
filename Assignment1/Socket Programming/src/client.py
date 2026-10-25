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

def receive_messages(sock):
  while True:
    try:
        message = sock.recv(1024)
        if not message:
            print("\nServer disconnected.")
            break
        #decode incoming bytes
        decoded = message.decode()
        print(f"\n{decoded}\nEnter command/message: ", end="", flush=True)
        
    except:
        break   



threading.Thread(
    target=receive_messages, args=(clientSocket,), daemon=True
).start()

print("Connected to chat/file server.")
print("Commands: 'status', 'list', 'get <filename>', 'exit', or any text for ACK.")

# main CLI input loop

while True:
    sentence = input("Enter command/message: ")
    if not sentence.strip():
        continue
    # send input to server
    clientSocket.send(sentence.encode())
    
    # user typed exit
    if sentence.lower() == 'exit':
        print("Disconnecting from server...")
        break



clientSocket.close()