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

HEADER_LENGTH = 20
IP = "127.0.0.1"
PORT = 12000

connectedClients = []
clientRecords = []


welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
welcomingSocket.bind((IP,PORT))
welcomingSocket.listen()


def handleClient(connectionSocket):
    addClient(connectionSocket)
    connectionSocket.send(f"You are Client {len(connectedClients)}".encode())
    
    while True:
        message = connectionSocket.recv(1024).decode().strip()
        if message:
            if message == "quit":
                break

            elif message == "records":
                connectionSocket.send(str(clientRecords).encode())
                continue

    
            for socket in connectedClients:
                socket.send(message)

        else:
            break
            
    removeClient(connectionSocket)
    connectionSocket.close()


def addClient(connectionSocket):
    connectedClients.append(connectionSocket)
    clientRecords.append({
        "socket": connectionSocket,
        "acceptedAt": datetime.now(),
        "finishedAt": None
    })


def removeClient(connectionSocket):
    connectedClients.remove(connectionSocket)
    for record in clientRecords:
        if record["socket"] == connectionSocket and record["finishedAt"] is None:
            record["finishedAt"] = datetime.now()


while True:
    connectionSocket, addr = welcomingSocket.accept()
    Thread(target=handleClient, args=(connectionSocket,), daemon=True).start()