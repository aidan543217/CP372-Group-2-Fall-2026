"""
-------------------------------------------------------
[This is the server function for a chat room]
-------------------------------------------------------
__updated__ = "2026-10-20"
-------------------------------------------------------
"""
# Imports
from socket import *
from threading import *
# Constants
HEADER_LENGTH = 20
IP = "127.0.0.1"
PORT = 12000

connectedClients = []


# Server socket setup
welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

welcomingSocket.bind((IP,PORT))
welcomingSocket.listen() # listen to the socket for updates


def handleClient(connectionSocket):
    connectedClients.append(connectionSocket)
    connectionSocket.send("Client connected, you may now begin chatting".encode())
    while True:
        message = connectionSocket.recv(1024)
        if message:
            for socket in connectedClients:
                socket.send(message)
    connectionSocket.close()



while True:
    connectionSocket, addr = welcomingSocket.accept()
    Thread(target=handleClient, args=(connectionSocket,), daemon=True).start()



