import socket
import threading
import json

from vault.data.datastore import DataStore
from vault.parser.parser import Parser


def handle_client(client_socket):
    # TODO: Add actual responses    
    
    while True:
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
            except Exception as e:
                #Catch security exceptions
                # send response
                client_send("{ Security Violation }".encode())
            

            # if command has exit or no more commands exit          

        else:
            #TODO: raise Error
            #pass
            break




    client_socket.close()


def start(port, password):
    print("server starting on port:", port)
    host = socket.gethostname()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('', port))
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
        #conn.settimeout(30)
        try:
            handle_client(client_socket)

            # client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            # client_handler.start()

        except :
            #TODO: Programm FAILED: the only status code sent back to the client is FAILED
            client_socket.send(json.loads({"status":"FAILED"}))
        
    client_socket.close()
