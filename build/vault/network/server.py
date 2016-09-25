import socket
import threading
import json
from vault.error import CmdError, NetworkError, SecurityError

def handle_client(client_socket):
    """
    Thread handler that manager 1 connection and close it
    """
    client_socket.setblocking(True)
    client_socket.settimeout(30)
    data = b''
    try:
        while not b'***' in data:
            tmp  = client_socket.recv(1024)
            if not tmp:
                break
            data += tmp
            print("[*] Received in socket", data)

        if data and b'***' in data:
            udata = data.decode()
            command = udata.split('***', 1)[0]
            print("[*] Received: \n%s" % command)


            try:
                #TODO: insert parser code here
                #Should return valid result or rise SecError
                #parser = Parser(command)

                #TODO: send value to client
                client_socket.send(b"good job slick")
            except SecurityError as e:
                print('EXCEPTION', e)
                client_socket.send("{exception}".encode())
    except socket.timeout  as e:
        print('socket timeout', e)
        client_socket.send(json.loads({"status":"Timeout"}))
    finally:
        client_socket.shutdown(socket.SHUT_WR)
        if not client_socket.recv(10):
            client_socket.close()





def start(port, password):
    print("server starting on port:", port)
    host = socket.gethostname()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('', port))
        server.listen(1)
    except OSError:
        raise CmdError(63, 'port is taken')
        socket.close()

    print("Listening on:", host, port)

    while True:
        (client_socket, address) = server.accept()
        print("[*] Accepted connection from: %s:%d" % (address[0], address[1]))
        try:
            #handle_client(client_socket)
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except Exception as e :
            print("FAILED", e)
            raise
    socket.close()
