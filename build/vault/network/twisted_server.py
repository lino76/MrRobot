"""
Event based simple TCP server - proof of concept
"""
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor

import simplejson as json

from vault.error import CmdError, NetworkError, SecurityError
from vault.core import Vault, Program


class TServer(Protocol):
    def __init__(self, vault):
        self.vault = vault

    def connectionLost(self, reason):
        print('connection lost ...',reason)

    def error_handler(self, exception):
        print(exception)
        print ('Connection lost somehow, nothing to do')

    def dataReceived(self, data):
        if data and b'***' in data:
            udata = data.decode()
            src = udata.split('***', 1)[0]
            program = Program(src)
            print("[*] Received: \n%s" % program.get_src())
            try:
                result = self.vault.run(program)
                self.transport.write(result.encode())
            except SecurityError as e:
                print('EXCEPTION', e)
                self.transport.write("{exception}".encode())


class ServerFactory(Factory):
    def __init__(self, vault):
        self.vault = vault

    def buildProtocol(self, address):
        print("[*] Accepted connection")
        return TServer(self.vault)


class Server:

    def __init__(self, password):
        self.vault = Vault(password)

    def start(self, port):
        try:
            print("server starting on port:", port)
            reactor.listenTCP(port, ServerFactory(self.vault))
            reactor.run()
        except Exception as e:
            print('Exception', e)
            raise CmdError(63, 'port is taken')
        print("Listening on:", port)

