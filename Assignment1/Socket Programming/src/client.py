import threading
from socket import *



serverName = "127.0.0.1"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

welcomeMessage = clientSocket.recv(1024).decode()
print("From Server:", welcomeMessage)

if welcomeMessage != "Connection was rejected as server is full":  


  while True:
    message = input("Enter a Message: ")
    
    clientSocket.send(message.encode())

    if message == "exit":
       break

    response = clientSocket.recv(1024).decode()

    if response:
      print("From Server:", response)

clientSocket.close()

