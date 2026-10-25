import threading
from socket import *



serverName = "127.0.0.1" # local host
serverPort = 12000 # port #1200
clientSocket = socket(AF_INET, SOCK_STREAM) 
clientSocket.connect((serverName,serverPort))

welcomeMessage = clientSocket.recv(1024).decode()
print("From Server:", welcomeMessage)

if welcomeMessage != "Connection was rejected as server is full":  

    if welcomeMessage.startswith("You are Client"):
       clientNo = welcomeMessage.split(" ")[3]
    print("'Help' for list of commands\n\n")

    while True:
        message = input("Enter a Message: ")
    
        clientSocket.send(message.encode())

        if message == "exit":
            break

        response = clientSocket.recv(1024).decode()
        if response:
            print("From Server:", response)
  

clientSocket.close()