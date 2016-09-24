import socket
import threading
import json

def handle_client(client_socket):
    # TODO: Add actual responses
    data = b''
    while not b'***' in data:
        tmp  = client_socket.recv(1024)
        if not tmp:
            break
        data += tmp
        print("[*] Received in socket", data)

        #TODO: It could issue the TIMEOUT status if input  with *** is not received within 30 seconds
    if data and b'***' in data:
        udata = data.decode("utf-8")
        commands = udata.split('***', 1)[0]
        print("[*] Received: %s" % commands)
    else:
        #TODO: raise Error
        pass
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
        print(OSError)
        #TODO: handle this
        #TODO: if port taken - the server should exit with code 63
        socket.close()

    print("Listening on:", host, port)

    while True:
        (client_socket, address) = server.accept()
        print("[*] Accepted connection from: %s:%d" % (address[0], address[1]))
        #TODO: It could issue the TIMEOUT status if input is not received within 30 seconds
        conn.settimeout(30)
        try:
            handle_client(client_socket)

            # client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            # client_handler.start()

        except :
            #TODO: Programm FAILED: the only status code sent back to the client is FAILED
            client_socket.send(json.loads({"status":"FAILED"}))
        finally:
            client_socket.close()
