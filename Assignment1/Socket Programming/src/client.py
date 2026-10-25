import threading
from socket import *


# AF_INET means IP networking, and SOCK_STREAM means TCP connection
serverName = "127.0.0.1"  # Localhost
serverPort = 12000         # The server's listening port
clientSocket = socket(AF_INET, SOCK_STREAM)

# Connect to the server and handle any connection errors
try:
    clientSocket.connect((serverName, serverPort))
except Exception as e:
    print(f"Unable to connect to server: {e}")
    exit()

# Wait for the server's first message, which should contain the assigned client name
# Converting text to bytes happens later; recv returns bytes and decode turns them into text
try:
    name_msg = clientSocket.recv(1024).decode()
except ConnectionResetError:
    print("Server closed the connection.")
    clientSocket.close()
    exit()
# Stop if the server is full
if name_msg == "SERVER_FULL":
    print("Server is full! Connection has been rejected.")
    clientSocket.close()
    exit()


# Confirm that the server sent a name assignment before continuing
if name_msg.startswith("NAME:"):
    # Remove the NAME: label and extra surrounding spaces from the received text
    client_name = name_msg[5:].strip()
    print(f"Assigned name: {client_name}")

    # Send the assigned name back so the server knows this client received it
    # encode converts readable text into bytes
    clientSocket.send(client_name.encode())
    print("Connected to chat/file server.\nCommands: 'status', 'list', 'get <filename>', 'exit', or any text for ACK.\nEnter command/message: ", end="", flush=True)

# This runs in the background and listens for replies from the server
def receive_messages(sock):
    while True:
        try:
            # recv waits for up to 1024 bytes and returns when server data arrives
            message = sock.recv(1024)

            # No bytes means the server closed the connection
            if not message:
                print("\nServer disconnected.")
                break

            # Convert received bytes into text and display them on the screen
            decoded = message.decode()
            print(f"\nServer: {decoded}\nEnter command/message: ", end="", flush=True)

        except OSError as e:
            # Prevents exit as being shown as error
            if not closing.is_set():
                print(f"Receive error: {e}")
            break
        except Exception as e:
            # States receive errors
            if not closing.is_set():
                print(f"Receive error: {e}")
            break

closing = threading.Event()

# Start the receiver in another thread while the main thread waits for typed commands
receiveThread = threading.Thread(
    target=receive_messages, args=(clientSocket,), daemon=True
)

receiveThread.start()


# Main loop to ask for commands until the user calls exit
while True:
    sentence = input()

    # Ignore empty lines
    if not sentence.strip():
        continue

    try:
        # Send the user's command as bytes
        clientSocket.send(sentence.encode())
    except Exception as e:
        print(f"Send error: {e}")
        break

    # Disconnect from server
    if sentence.lower() == "exit":
        print("Disconnecting from server...")
        break



closing.set()
clientSocket.shutdown(SHUT_RDWR)
clientSocket.close()
receiveThread.join(timeout=1) # allows thread to finish before python quits