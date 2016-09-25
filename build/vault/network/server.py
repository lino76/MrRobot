import socket
import threading
import json

def handle_client(client_socket):
    # TODO: Add actual responses

    client_socket.settimeout(30)
    data = b''
    while not b'***' in data:
        tmp  = client_socket.recv(1024)
        if not tmp:
            break
        data += tmp
        print("[*] Received in socket", data)

            #TODO: It could issue the TIMEOUT status if input  with *** is not received within 30 seconds
    if data and b'***' in data:
        udata = data.decode()
        command = udata.split('***', 1)[0]
        print("[*] Received: \n%s" % command)

        # Parse and process command
        try:
            #parser = Parser(command)
            # pass return the return value
            client_socket.send("good job slick".encode())
            print("[*] Sended")
        except Exception as e:
            #TODO Catch security exceptions
            # send response
            client_socket.send("{exception}".encode())
    else:
        #TODO: Send time-out
        pass






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
        #client_socket.settimeout(30)
        try:
            handle_client(client_socket)

            # client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            # client_handler.start()

        except Exception as e :
            print("FAILED", e)
            client_socket.send(json.loads({"status":"FAILED"}))
        client_socket.close()
    socket.close()
