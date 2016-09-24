import socket
import threading


def handle_client(client_socket):
    # TODO: Add actual responses
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)
    client_socket.send("ACK!")
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
