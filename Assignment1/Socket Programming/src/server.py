"""
-------------------------------------------------------
[This is the server function for a chat room]
-------------------------------------------------------
__updated__ = "2026-10-24"
-------------------------------------------------------
"""
from datetime import datetime
import os
from socket import *
from threading import Thread


IP = "127.0.0.1"      # Localhost
PORT = 12000          # The port
MAX_CLIENTS = 3       
REPO_DIR = "./repo"   # Repo folder containing files clients can get by default

# Make sure the repository folder exists before the server uses it
if not os.path.exists(REPO_DIR):
    os.makedirs(REPO_DIR)
    with open(os.path.join(REPO_DIR, "repo1.txt"), "w") as f:
        f.write("Server repository file 1")
    with open(os.path.join(REPO_DIR, "repo2.txt"), "w") as f:
        f.write("Server repository file 2")

connectedClients = []
client_cache = []      # Connection details kept for the status command
client_counter = 0     # Client name counter to assign unique names


# Create the server's welcome socket
welcomingSocket = socket(AF_INET, SOCK_STREAM)

# Allow a quick restart when the server was using this address recently
welcomingSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# Reserve the address and port, then start accepting incoming clients
welcomingSocket.bind((IP, PORT))
welcomingSocket.listen()


# Communicates with one client inside its own thread
def handleClient(connectionSocket, addr, client_name):
    global connectedClients, client_cache

    # Record when this client first connected.
    connect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session_info = {
        "name": client_name,
        "address": str(addr),
        "connected_at": connect_time,
        "finished_at": "Active",
    }
    
    # Store the new session in memory so status can display it later
    client_cache.append(session_info)

    try:
        # Keep listening for commands from this client until disconnect
        while True:
            # recv waits for incoming bytes up to 1024 bytes
            data = connectionSocket.recv(1024)
            if not data:
                break

            # Decode message into readable text
            message = data.decode().strip()
            print(f"[{client_name}] {message}")

            if message.lower() == "exit":
                connectionSocket.close()
                break

            elif message.lower() == "status":
                cache_str = "\n--- Server Connection Cache ---\n"
                for entry in client_cache:
                    cache_str += (
                        f"Name: {entry['name']} | IP: {entry['address']} | Connected:"
                        f" {entry['connected_at']} | Finished: {entry['finished_at']}\n"
                    )
                connectionSocket.send(cache_str.encode())

            elif message.lower() == "list":
                files = os.listdir(REPO_DIR)
                file_list_str = (
                    "Files in Repository:\n" + "\n".join(files)
                    if files
                    else "Repository is empty."
                )
                connectionSocket.send(file_list_str.encode())
            
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

            else:
                response = f"Echo: {message} ACK"
                connectionSocket.send(response.encode())
    except Exception as e:
        print(f"Error with {client_name}: {e}")
    finally:
        # Clean up session when client disconnects
        disconnect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if connectionSocket in connectedClients:
            connectedClients.remove(connectionSocket)
        for entry in client_cache:
            if entry["name"] == client_name and entry["finished_at"] == "Active":
                entry["finished_at"] = disconnect_time
                break
        print(f"{client_name} has disconnected at {disconnect_time}")
        connectionSocket.close()
            
print(f"Server listening on {IP}:{PORT} (Max Clients: {MAX_CLIENTS})")

# Waiting loop for clients to call the server
while True:
    # accept blocks until a client connects and then return that client's socket and address
    connectionSocket, addr = welcomingSocket.accept()
    print(f"Connection accepted from {addr}")

    print(f"Current clients: {len(connectedClients)}")
    # Server full handling
    if len(connectedClients) >= MAX_CLIENTS:
        connectionSocket.send("SERVER_FULL".encode())
        connectionSocket.close()
        continue

    # Give client a name assignment
    client_counter += 1
    client_name = f"Client{client_counter:02d}"

    # Send the name assignment and wait for the client to acknowledge it before adding them to the connected clients list
    connectionSocket.send(f"NAME:{client_name}".encode())
    received_name = connectionSocket.recv(1024).decode().strip()
    if received_name == client_name:
        print(f"{client_name} acknowledged assigned name")
        connectedClients.append(connectionSocket)

    # Give a client a separate thread so another client can connect to the server at the same time
    Thread(
        target=handleClient,
        args=(connectionSocket, addr, client_name),
        daemon=True,
    ).start()
                