import threading
from socket import *



serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

ConnectedClients = []

def receive_messages(sock):
  while True:
    message = sock.recv(1024).decode()
    if message:
      print("From Server:", message)


threading.Thread(
    target=receive_messages, args=(clientSocket,), daemon=True
).start()

while True:
    sentence = input()
    clientSocket.send(sentence.encode())



clientSocket.close()

