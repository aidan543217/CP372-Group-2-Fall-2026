from socket import *



serverName = "127.0.0.1" # local host
serverPort = 12000 # port #1200
clientSocket = socket(AF_INET, SOCK_STREAM) 
clientSocket.connect((serverName,serverPort))

welcomeMessage = clientSocket.recv(1024).decode()
print("From Server:", welcomeMessage)

if welcomeMessage != "Connection was rejected as server is full":  

    clientSocket.send(welcomeMessage.split(" ")[2].encode()) # send the client number contained in the welcome message

    print("Available commands: list, get <filename>, status, exit\n")

    while True:
        message = input("Enter a Message: ")

        if not message.strip(): # sending an empty string would cause issues in the server, so it should just reprompt
            continue

        clientSocket.send(message.encode())

        if message == "exit":
            break

        if message.lower().startswith("get "):
            initial_response = clientSocket.recv(1024)
            
            if initial_response.startswith(b"File not found"):
                print("From Server:", initial_response.decode())
            else:
                chunks = [initial_response]
                clientSocket.settimeout(0.5) # brief timeout to catch the end of the stream
                try:
                    while True:
                        chunk = clientSocket.recv(1024)
                        if not chunk:
                            break
                        chunks.append(chunk)
                except timeout:
                    pass
                clientSocket.settimeout(None) # reset timeout back to normal blocking
                
                # Combine all chunks together and decode
                full_file_data = b"".join(chunks)
                print("From Server File Content:\n" + full_file_data.decode())
        else:
            response = clientSocket.recv(1024).decode()
            print("From Server:", response)
  
    clientSocket.close()