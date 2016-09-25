import socket
import threading
from vault.data.datastore import DataStore
from vault.parser.parser import Parser

datastore

def handle_client(client_socket):
    # TODO: Add actual responses
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)

    # Probably this needs to be a singleton that gets reset every time
    datastore = DataStore()

    try:
        parser = Parser("Pass string in here")
        # pass return the return value
        client_socket.send("good job slick")
    except Exception as e:
        #Catch security exceptions
        client_send("{ Security Violation }")
    
    client_socket.close()


def start(port, password):
    print("server starting on port:", port)
    host = socket.gethostname()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
        server.listen(1)
    except OSError:
        print("whoops server startup error")
        print(OSError)
        #TODO handle this
        socket.close()

    print("Listening on:", host, port)

    while True:
        (client_socket, address) = server.accept()
        print("[*] Accepted connection from: %s:%d" % (address[0], address[1]))
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()
