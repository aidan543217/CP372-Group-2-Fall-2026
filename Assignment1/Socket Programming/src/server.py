"""
-------------------------------------------------------
[This is the server function for a chat room]
-------------------------------------------------------
__updated__ = "2026-10-24"
-------------------------------------------------------
"""
# Imports
from datetime import datetime
import os
from socket import *
from threading import *
# Constants

IP = "127.0.0.1"
PORT = 12000
MAX_CLIENTS = 3 # hardcoded value
REPO_DIR = "./repo" # server repository directory

# ensure file directory exists
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)
    with open(os.path.join(REPO_DIR, "test1.txt"), "w") as f:
        f.write("Server repository file 1")
    with open(os.path.join(REPO_DIR, "test2.txt"), "w") as f:
        f.write("Server repository file 2")

# shared threading synchronization
connect_clients_lock = Lock() # prevents race conditions when modifying shared lists
connectedClients = []# tracks active client sockets
client_cache = (
    []
) # in-memory cache holding details and timestamps
client_counter = (
    0
) # used to generate incremental names


# Server socket setup
welcomingSocket = socket(AF_INET,SOCK_STREAM)
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

welcomingSocket.bind((IP,PORT))
welcomingSocket.listen() # listen to the socket for updates


def handleClient(connectionSocket, addr, client_name):
    # Handles individual client communication in a seperate thread
    global connected_clients, client_cache
    
    # connection timestamp
    connect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_info = {
        "name": client_name,
        "address": str(addr),
        "connected_at": connect_time,
        "finished_at": "Active",
    }
    
    with connect_clients_lock: # safely add to shared tracking structures
        connectedClients.append(connectionSocket)
        client_cache.append(session_info)
    
    connectionSocket.send("Client connected, you may now begin chatting".encode())
    
    try:
        while True:
            data = connectionSocket.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            
            # handle 'exit'
            if message.lower() == "exit":
                connectionSocket.send("ACK_EXIT".encode())
                break
            # handle 'status'
            elif message.lower() == "status":
                cache_str = "\n--- Server Connection Cache ---\n"
                for entry in client_cache:
                    cache_str += (
                        f"Name: {entry['name']} | IP: {entry['address']} | Connected:"
                        f" {entry['connected_at']} | Finished: {entry['finished_at']}\n"
                    )
                connectionSocket.send(cache_str.encode())
            # handle 'list'
            elif message.lower() == 'list':
                files = os.listdir(REPO_DIR)
                file_list_str = (
                    "Files in Repository:\n" + "\n".join(files)
                    if files
                    else "Repository is empty."
                )
                connectionSocket.send(file_list_str.encode())
            
            # handle file streaming get <filename>
            
            elif message.startswith("get "):
                filename = message[4:].strip()
                filepath = os.path.join(REPO_DIR, filename)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        chunk = f.read(1024)
                        while chunk:
                            connectionSocket.send(chunk)
                            chunk = f.read(1024)
                else:
                    connectionSocket.send(f"Error: File '{filename}' not found.".encode())
            # Standard message: echo back "ACK"
            else:
                response = f"Echo: {message} ACK"
                connectionSocket.send(response.encode())
    except Exception as e:
        print(f"Error with {client_name}: {e}")
    finally:
        # update cache with finish time
        disconnect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with connect_clients_lock:
            if connectionSocket in connectedClients:
                connectedClients.remove(connectionSocket)
            for entry in client_cache:
                if entry["name"] == client_name and entry["finished_at"] == "Active":
                    entry["finished_at"] = disconnect_time
                    break
            connectionSocket.close()
            
print(f"Server listening on {IP}:{PORT} (Max Clients: {MAX_CLIENTS})")
    
while True:
    connectionSocket, addr = welcomingSocket.accept()
        
    #enforce max clients limit and incremental naming
    with connect_clients_lock:
        if len(connectedClients) >= MAX_CLIENTS:
            connectionSocket.send(
                "Server full! Connection rejected.")
    
            connectionSocket.close()
            continue
        client_counter += 1
        client_name = f"Client{client_counter:02d}"
        
    # pass socket, address, and name into thread
    Thread(target=handleClient, args=(connectionSocket, addr, client_name), daemon=True,).start()
                