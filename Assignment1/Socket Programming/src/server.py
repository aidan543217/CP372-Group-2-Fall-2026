"""
-------------------------------------------------------
[This is the server function for a chat room]
-------------------------------------------------------
__updated__ = "2026-10-20"
-------------------------------------------------------
"""
from socket import *
from threading import *
from datetime import datetime

IP = "127.0.0.1"
PORT = 12000

connectedClients = []
clientRecords = []
maxClients = 3


welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
welcomingSocket.bind((IP,PORT))
welcomingSocket.listen()


def handleClient(connectionSocket, address):

    addClient(connectionSocket, address)
    connectionSocket.send(f"You are Client {len(connectedClients)}".encode())
    
    while True:
        message = connectionSocket.recv(1024).decode().strip()
        if message:
            if message == "exit":
                break

            elif message == "status":
                connectionSocket.send(str(clientRecords).encode())
                continue

            elif message == "list":

                continue

            else:
                response_message = f"{message} ACK"
                connectionSocket.send(response_message.encode())

        else:
            break
            
    removeClient(connectionSocket, address)
    connectionSocket.close()


def addClient(connectionSocket, address):
    connectedClients.append(connectionSocket)

    clientIP, clientPort = address
    clientRecords.append({
        "ip": clientIP,
        "port": clientPort,
        "acceptedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "finishedAt": None
    })


def removeClient(connectionSocket, address):
    connectedClients.remove(connectionSocket)

    clientIP, clientPort = address
    for record in clientRecords:
        if record["ip"] == clientIP and record["port"] == clientPort and record["finishedAt"] is None:
            record["finishedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


while True:
    connectionSocket, address = welcomingSocket.accept()

    # putting the max client logic here so that a thread doesnt need to be created and immediately removed
    if len(connectedClients) >= maxClients:
        print(f"Connection from {address} rejected as server is full.")
        connectionSocket.send("Connection was rejected as server is full".encode())
        connectionSocket.close()
        continue

    Thread(target=handleClient, args=(connectionSocket,address), daemon=True).start()