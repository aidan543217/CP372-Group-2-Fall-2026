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
import os # for IO input output operations

IP = "127.0.0.1" # local host
PORT = 12000 # port 1200

connectedClients = []
clientRecords = []
maxClients = 3
repoDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo") # repo in same directory as server.py

# make repository directory
if not os.path.exists(repoDir):
    os.makedirs(repoDir)
    with open(os.path.join(repoDir, "text1.txt"), "w") as f:
        f.write("This is text1\n")
    with open(os.path.join(repoDir, "text2.txt"), "w") as f:
        f.write("Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Duis tellus. Donec sollicitudin mi sit amet mauris.\nNam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus.\nDonec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien.\nDuis lobortis massa imperdiet quam. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper.\nAenean ultricies mi vitae est. Mauris placerat eleifend leo.\n")



welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allow for address reuse
welcomingSocket.bind((IP,PORT))
welcomingSocket.listen()
def handleClient(connectionSocket, address):

    try:
        addClient(connectionSocket, address)
        connectionSocket.send(f"You are Client {len(connectedClients)}".encode())
        print(f"Connection from {address} accepted. Client {len(connectedClients)} connected.")
        
        while True:
            message = connectionSocket.recv(1024).decode().strip() #decode the message that was sent
            if message:
                checkMessage = message.lower()
                if checkMessage == "exit":
                    break

                elif checkMessage == "status":
                    connectionSocket.send(str(clientRecords).encode())
                    continue

                elif checkMessage == ("list"):
                    files = os.listdir(repoDir)
                    if files: # check if files exist in the repo directory
                        file_list = ("\n".join(files)).encode()
                    else: # no files exist in the repo directory
                        file_list = "No files found".encode()
                    connectionSocket.send(file_list)
                    
                    continue
                elif checkMessage.startswith("get "): # space is needed so it doesnt crash
                    filename = message.split(" ")[1].strip() # get the filename from the message
                    filePath = os.path.join(repoDir, filename)
                    if os.path.exists(filePath) and os.path.isfile(filePath):
                        with open(filePath, "r") as f:
                            fileContent = f.read()
                        connectionSocket.send(fileContent.encode())
                    else:
                        connectionSocket.send("File not found".encode())
                elif checkMessage == "help":
                    connectionSocket.send("Available commands: list, get <filename> or <filepath>, status, exit".encode())

                else:
                    response_message = f"{message} ACK"
                    connectionSocket.send(response_message.encode())
                    print(f"\nMessage from {address}: {message}")

            else:
                break
    finally:
            
        removeClient(connectionSocket, address)
        connectionSocket.close()


def addClient(connectionSocket, address):
    connectedClients.append(connectionSocket) # append the connection socket to the list of connected clients

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
            print(f"Client {len(connectedClients)+1} from {address} disconnected at {record['finishedAt']}.")


while True:
    connectionSocket, address = welcomingSocket.accept()

    # putting the max client logic here so that a thread doesnt need to be created and immediately removed
    if len(connectedClients) >= maxClients:
        print(f"Connection from {address} rejected as server is full.")
        connectionSocket.send("Connection was rejected as server is full".encode())
        connectionSocket.close()
        continue

    Thread(target=handleClient, args=(connectionSocket,address), daemon=True).start()