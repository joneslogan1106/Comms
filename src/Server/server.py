import threading, socket, time, db, os, importlib
from c16 import ctypes, c16
exiting = False
clients = []
debug = 0
if __name__ == "__main__":
    def load_mods():
        for file in os.listdir("mods"):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                importlib.import_module(f"mods.{module_name}")
    def glue(i: list, s: str = " "):
        o = ""
        for v in i:
            o += v + s
        return o[:-1]
    def fix_string(i: str):
        o = ""
        replace_string_list = {
            "\n": "\\n",
            "\\": "\\\\"
        }
        for v in i:
            try:
                o += replace_string_list[v]
            except KeyError:
                o += v
        return o
    def listen_messages(client):
        PORT = 9980
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        server_socket.bind((client, PORT))
        server_socket.listen(3) # we listen and we judge
        print(f"[SERVER]: Listening for messages on {client}:{PORT}")
        while not exiting:
            client, addr = server_socket.accept() # yayyyyyyyyyyyyyy
            data = client.recv(1024)
            data = fix_string(data.decode()).split(";")
            if db.validate_message(f"0;0;{glue(data, ";")}"):
                db.add_message(str(time.time()), data[0], glue(data[1:]))
                print(f"[SERVER]: Received message from {addr}: {data}")
            client.send(b"Thx")
    def get_new_chats(timed):
        messages = ""
        f = open("database.db", "r")
        for i in f.readlines():
            if db.fetch_time(i) >= timed:
                messages += i + "\n"
        return messages
    def send_messages(client, timed):
        PORT = 6090
        chats = get_new_chats(timed)
        message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        message_socket.connect((client, PORT))
        message_socket.sendall(chats.encode())
    def authentication(client: str):
        PORT = 12090
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        server_socket.connect((client, PORT))
        server_socket.send(b"Authed")
    def acception():
        try:
            HOST = "127.0.0.1"
            PORT = 10740
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            authentication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            authentication_socket.bind((HOST, 9281))
            authentication_socket.listen(1)
            print("[SERVER]: Started authentication socket")
            print(f"[SERVER]: Listening on {HOST}:{PORT}")
            while not exiting:
                client, addr = server_socket.accept()
                client.recv(1024)
                authentication_socket.recv(1024)
                timed = time.time()
                client.send(b"Pong")
                authentication_socket.send(b"Auth1")
                global clients
                clients.append(addr[0])
                print(f"[SERVER]: New client connected: {addr}")
                print(f"[SERVER]: Addr: {addr}")
                threading.Thread(target=heartbeat, args=(addr[0],)).start()
                threading.Thread(target=listen_messages, args=(addr[0],)).start()
                #client.close()
        except KeyboardInterrupt:
            server_socket.close()
            exit()
    def heartbeat(client):
        while not exiting:
                PORT = 8070
                heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                heartbeat_socket.settimeout(5)
                global clients
                try:
                    heartbeat_socket.connect((client, PORT))
                except ConnectionRefusedError:
                    print(client)
                    clients.remove(client)
                    print("Connection Refused1")
                    
                    return
                #try:
                    #heartbeat_socket.bind((client, PORT))
                #except ConnectionRefusedError:
                    #print("Connection Refused2")
                    #clients.remove(client)
                    #return
                time.sleep(0.15)
                try:
                    heartbeat_socket.sendall(b"Ping")
                    try:
                        data = float(heartbeat_socket.recv(1024).decode())
                    except:
                        continue
                except TimeoutError:
                    print("Connection Timed Out")
                    clients.remove(client)
                    
                    return
                except BrokenPipeError:
                    print("Pipe Broke")
                    clients.remove(client)
                    return
                except TypeError:
                    print("Faulty Client, Float not recieved")
                    clients.remove(client)
                    return
                except ConnectionResetError:
                    print("Faulty Client, Killed Connection")
                    clients.remove(client)
                    return
                threading.Thread(target=send_messages, args=(client, data))
                heartbeat_socket.close()
    thread = threading.Thread(target=acception)
    thread.start()
    while True:
        time.sleep(0.2)
        threads = []
        if debug == 1:
            print(clients)
            
