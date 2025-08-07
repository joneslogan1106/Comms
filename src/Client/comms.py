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
        except Exception as e:
            print(f"Heartbeat error: {e}")
            break
    client.close()

def main():
    HOST = "127.0.0.1"
    PORT = 10740
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.sendall(b"Ping")
    client_socket.settimeout(5)
    try:
        data = client_socket.recv(1024)
    except TimeoutError:
        exit("Connection Refused.")
    if data == b"Pong":
        print("Connected")
        threading.Thread(target=heartbeat, daemon=True).start()
        threading.Thread(target=fetch_messages, daemon=True).start()
        while True:
            send_message()
    else:
        exit("Connection Refused.")

if __name__ == "__main__":
    main()