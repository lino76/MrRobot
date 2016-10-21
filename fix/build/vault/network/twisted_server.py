"""
Event based simple TCP server - proof of concept
"""
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor, defer
from twisted.internet.error import CannotListenError

import simplejson as json

from vault.error import CmdError, NetworkError, SecurityError
from vault.core import Vault, Program
import signal

class TServer(Protocol):
    def __init__(self, vault):
        self.vault = vault

    def connectionLost(self, reason):
        print('connection lost ...', reason)

    def error_handler(self, exception):
        #print(exception)
        print('Connection lost somehow, nothing to do')
        reactor.stop()


    def dataReceived(self, data):
        if data and b'***' in data:
            udata = data.decode()
            src = udata.split('***', 1)[0]
            program = Program(src)
            print("[*] Received: \n%s" % program.get_src())
            try:
                result = self.vault.run(program)
                self.transport.write(result.encode())
            except:
                # print('EXCEPTION', e)
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

    def stop(self, _signo):
        if reactor.running:
            if _signo == signal.SIGTERM:
                reactor.callFromThread(reactor.sigTerm)
            elif _signo == signal.SIGINT:
                reactor.callFromThread(reactor.sigInt)
            else:
                reactor.callFromThread(reactor.stop)

    def start(self, port):
        try:
            print("server starting on port:", port)
            reactor.listenTCP(port, ServerFactory(self.vault))
        except CannotListenError:
            raise NetworkError(63, 'port is taken')

        try:
            reactor.run(installSignalHandlers=False)
        except:
            raise NetworkError(0, 'reactor error')
