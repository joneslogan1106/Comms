import threading, socket, time, db
from c16 import ctypes, c16
exiting = False
clients = []
debug = 1
if __name__ == "__main__":
    def get_new_chats(timed):
        messages = []
        f = open("database.db", "r")
        for i in f.readlines():
            if db.fetch_time(i) >= timed:
                messages.append(i)
        return messages
    def send_messages(client, timed):
        PORT = 6090
        chats = get_new_chats(timed)
        message_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        message_socket.connect((client, PORT))
        message_socket.sendall(str(chats).encode())
    def acception():
        try:
            HOST = "127.0.0.1"
            PORT = 10740
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            server_socket.bind((HOST, PORT))
            server_socket.listen(5)
            while not exiting:
                client, addr = server_socket.accept()
                client.recv(1024)
                timed = time.time()
                client.send(b"Pong")
                global clients
                clients.append(addr[0])
                print(f"[SERVER]: New client connected: {addr}")
                print(f"[SERVER]: Addr: {addr}")
                threading.Thread(target=heartbeat, args=(addr[0],)).start()
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
                send_messages(client, data)
                heartbeat_socket.close()
    thread = threading.Thread(target=acception)
    thread.start()
    while True:
        time.sleep(0.2)
        threads = []
        if debug == 1:
            print(clients)
            
