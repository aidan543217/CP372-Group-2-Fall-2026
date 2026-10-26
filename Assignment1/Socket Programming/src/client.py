from socket import *

serverName = "127.0.0.1" # local host
serverPort = 12000 # port #1200
clientSocket = socket(AF_INET, SOCK_STREAM) 
clientSocket.connect((serverName,serverPort))


welcomeMessage = clientSocket.recv(1024).decode()
print("From Server:", welcomeMessage)

if welcomeMessage != "Connection was rejected as server is full":
    clientSocket.send(welcomeMessage.split(" ")[3].encode()) # send the client number contained in the welcome message

    print("Available commands: list, get <filename>, status, exit\n")

    while True:
        message = input("Enter a Message: ")

        if not message.strip(): # sending an empty string would cause issues in the server, so client should just reprompt
            continue

        clientSocket.send(message.encode())

        # allow the process to terminate
        if message == "exit":
            break

        # filestreaming
        if message != "get " and message.startswith("get "):
            initialResponse = clientSocket.recv(1024)
            
            if initialResponse.decode().startswith("File not found"):
                print("From Server:", initialResponse.decode())

            else:
                chunks = [initialResponse]
                clientSocket.settimeout(0.5) # using timeout to catch the end of the stream
                try:
                    while True:
                        chunk = clientSocket.recv(1024)
                        if not chunk:
                            break
                        chunks.append(chunk)
                except timeout:
                    pass
                clientSocket.settimeout(None)
                
                # combine all the chunks
                fullData = type(chunks[0])().join(chunks)
                print("From Server:\n" + fullData.decode())

        else:
            response = clientSocket.recv(1024).decode()
            print("From Server:", response)
  
    clientSocket.close()