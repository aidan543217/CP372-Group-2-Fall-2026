from socket import *
from threading import *
from datetime import datetime
import os

IP = "127.0.0.1"
PORT = 12000

connectedClients = []
clientStatuses = []
maxClients = 3

# resolve the path relative to this file instead of what file the user is in
repoDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo") 


welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.bind((IP,PORT))
welcomingSocket.listen()


def handleClient(connectionSocket, address):
    # guarantees that cleanup logic will occur even if the thread terminates due to an error
    try:
        addClient(connectionSocket, address)
        connectionSocket.send(f"You are Client {len(connectedClients)}".encode())

        id = connectionSocket.recv(1024).decode()
        print(f"Connection from {str(address[0])+":"+str(address[1])} accepted. Client {id} connected.")

        while True:
            message = connectionSocket.recv(1024).decode().strip() #decode the message that was sent

            if message:
                checkMessage = message.lower()
                if checkMessage == "exit":
                    break

                elif checkMessage == "status":
                    connectionSocket.send(str(clientStatuses).encode())
                    continue

                elif checkMessage == ("list"):
                    files = os.listdir(repoDir)

                    if files:
                        fileList = ("\n".join(files)).encode()
                    else:
                        fileList = "No files found".encode()

                    connectionSocket.send(fileList)
                    continue

                elif checkMessage.startswith("get "): # get <filename>
                    # check if the client message is exactly "get "
                    parts = message.split(" ")
                    if len(parts) < 2 or not parts[1].strip():
                        connectionSocket.send("Invalid get command. Usage is: get <filename>".encode())
                        continue

                    filename = message.split(" ")[1].strip() # get the filename from the message
                    filePath = os.path.join(repoDir, filename)

                    if os.path.exists(filePath) and os.path.isfile(filePath):
                        with open(filePath, "rb") as f:
                            # in case the message is more than 1024 bytes, send the contents via streaming
                            while True:
                                chunk = f.read(1024)
                                if not chunk:
                                    break
                                connectionSocket.send(chunk)
                    else:
                        connectionSocket.send("File not found".encode())
                        
                else:
                    connectionSocket.send(f"{message} ACK".encode())
                    print(f"Message from {str(address[0])+":"+str(address[1])}: {message}")

            else: # this case occurs
                break

    except (ConnectionResetError, ConnectionAbortedError):
        print(f"Client from {str(address[0])+":"+str(address[1])} abruptly disconnected.")

    finally:
        removeClient(connectionSocket, address)
        connectionSocket.close()


def addClient(connectionSocket, address):
    connectedClients.append(connectionSocket)

    clientStatuses.append({
        "address": str(address[0])+":"+str(address[1]),
        "acceptedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "finishedAt": None
    })


def removeClient(connectionSocket, address):
    connectedClients.remove(connectionSocket)

    for status in clientStatuses:
        if status["address"] == str(address[0])+":"+str(address[1]) and status["finishedAt"] is None:
            status["finishedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Client {len(connectedClients)+1} from {str(address[0])+":"+str(address[1])} disconnected at {status['finishedAt']}.")


while True:
    connectionSocket, address = welcomingSocket.accept()

    # putting the max client logic here so that a thread doesnt need to be created and immediately removed
    if len(connectedClients) >= maxClients:
        print(f"Connection from {str(address[0])+":"+str(address[1])} rejected as server is full.")
        connectionSocket.send("Connection was rejected as server is full".encode())
        connectionSocket.close()
        continue

    Thread(target=handleClient, args=(connectionSocket,address)).start()