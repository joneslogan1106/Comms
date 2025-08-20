import threading, socket, time, db, ast
from prompt_toolkit import PromptSession
from time import sleep
past_time = 0
session = PromptSession()
username = "Bob"
def unfix_message(i: str):
    o = ""
    b = False
    replace_list = {
        "n":"\n",
        "\\": "\\"
    }
    for v in i:
        if b:
            try:
                o += replace_list[v]
            except KeyError:
                o += v
            b = False
        elif v == "\\":
            b = True
        else:
            o += v
    return o
def fetch_messages():
    HOST = "127.0.0.1"
    PORT = 6090
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    while True:
        client, addr = server_socket.accept()
        try:
            messages = client.recv(4096)
            # Decode bytes to string before splitting
            messages_str = messages.decode()
            for i in messages_str.split("\n"):
                print(f"{db.fetch_user(i)}: {unfix_message(db.fetch_message(i))}")
        except Exception as e:
            print(f"Error in fetch_messages: {e}")
        finally:
            client.close()

def send_message():
    print("Press [Alt/Option+Enter] or [Esc] followed by [Enter] to accept input.")
    message = session.prompt("Enter message: ", multiline=True)
    message = str(message)
    HOST = "127.0.0.1"
    PORT = 9980
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(f"{username};{message}".encode())
    client_socket.close()

def heartbeat():
    HOST = "127.0.0.1"
    PORT = 8070
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(3)
    while True:
        try:
            client, addr = server_socket.accept()
            data = client.recv(1024)
            tries = 10
            while not data and tries > 0:
                data = client.recv(1024)
                tries -= 1
            client.sendall(str(time.time()).encode("utf-8"))
            client.close()  # Close client connection after each heartbeat
        except Exception as e:
            print(f"Heartbeat error: {e}")
            break
    server_socket.close()

def main():
    HOST = "127.0.0.1"
    PORT = 10740
    AUTH_PORT = 9281
    
    # Step 1: Set up client listening socket for server's authentication callback first
    client_auth_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_auth_listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_auth_listener.bind((HOST, 12090))
    client_auth_listener.listen(1)
    client_auth_listener.settimeout(10)
    
    # Step 2: Connect to main server socket
    print("Connecting to main server socket...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    print("Sending Ping...")
    client_socket.sendall(b"Ping")
    
    # Step 3: Connect to authentication socket simultaneously
    print("Connecting to authentication socket...")
    auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    auth_socket.connect((HOST, AUTH_PORT))
    print("Sending AuthRequest...")
    auth_socket.sendall(b"AuthRequest")
    
    # Step 4: Wait for server responses
    try:
        # Server should send "Pong" on main socket
        client_socket.settimeout(5)
        data = client_socket.recv(1024)
        
        # Server should send "Auth1" on auth socket  
        auth_socket.settimeout(5)
        auth_response = auth_socket.recv(1024)
        
        if data == b"Pong" and auth_response == b"Auth1":
            print("Connected and authenticated with server")
            
            # Step 5: Wait for server's authentication callback
            try:
                server_conn, addr = client_auth_listener.accept()
                server_auth_data = server_conn.recv(1024)
                if server_auth_data == b"Authed":
                    print("Full authentication completed")
                    server_conn.close()
                    client_auth_listener.close()
                    auth_socket.close()
                    client_socket.close()
                    
                    # Start client threads
                    threading.Thread(target=heartbeat, daemon=True).start()
                    threading.Thread(target=fetch_messages, daemon=True).start()
                    
                    print("Client ready - you can start sending messages")
                    while True:
                        send_message()
                else:
                    exit("Server authentication callback failed.")
            except TimeoutError:
                exit("Server authentication callback timeout.")
        else:
            exit("Authentication Failed.")
            
    except TimeoutError:
        exit("Connection timeout during authentication.")
    except Exception as e:
        exit(f"Authentication error: {e}")
    finally:
        # Clean up sockets
        try:
            client_socket.close()
            auth_socket.close() 
            client_auth_listener.close()
        except:
            pass

if __name__ == "__main__":
    main()