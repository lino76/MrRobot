import socket

def clientSend(port, data):
    conn = socket.socket()
    conn.connect((socket.gethostname(), port))
    print('[*] Client sending data', data)
    conn.send(data)

    data = b""
    tmp = conn.recv(1024)
    while tmp:
        data += tmp
        tmp = conn.recv(1024)
    print('[*] Client received response', data)
    conn.close()


if __name__ == '__main__':
    clientSend(1024,b'Helo***')
