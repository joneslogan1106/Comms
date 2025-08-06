import threading, socket, time, db, ast, json
from time import sleep
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
            # Expecting JSON-encoded list of messages
            msgs = json.loads(messages.decode())
            with open("cdatabase.db", "a") as f:
                for msg in msgs:
                    f.write(msg + "\n")
        except Exception as e:
            print(f"Error in fetch_messages: {e}")
        finally:
            client.close()

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
            print(data)
            tries = 10
            while not data and tries > 0:
                data = client.recv(1024)
                print(f"Empty data recieved, Tries left: {str(tries)}")
                sleep(0.5 * (11-tries))
                tries -= 1
            client.sendall(str(time.time()).encode("utf-8"))
            print(data.decode("utf-8"))
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
        print("PONG!")
        threading.Thread(target=heartbeat, daemon=True).start()
        threading.Thread(target=fetch_messages, daemon=True).start()
        while True:
            time.sleep(1)
    else:
        exit("Connection Refused.")

if __name__ == "__main__":
    main()