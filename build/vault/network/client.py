import socket
host = ''
port = 1024

def clientSend(data):
    conn = socket.socket()
    conn.connect((host, port))
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
    clientSend(b'Helo***')
