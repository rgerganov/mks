import urlparse
import websockify
import socket
import ssl
import base64
import hashlib
import string
import random

class AuthdRequestHandler(websockify.ProxyRequestHandler):

    def new_websocket_client(self):
        parse = urlparse.urlparse(self.path)
        query = parse.query
        args = urlparse.parse_qs(query)
        host = args.get("host", [""]).pop()
        port = args.get("port", [""]).pop()
        port = int(port)
        ticket = args.get("ticket", [""]).pop()
        cfgFile = args.get("cfgFile", [""]).pop()
        thumbprint = args.get("thumbprint", [""]).pop()
        thumbprint = thumbprint.replace(':', '').lower()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        line = sock.recv(1024)
        print line
        sock = ssl.wrap_socket(sock)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        cert = sock.getpeercert(binary_form=True)
        h = hashlib.sha1()
        h.update(cert)
        if thumbprint != h.hexdigest():
            raise Exception("Server thumbprint doesn't match")
        sock.write("USER %s\r\n" % ticket)
        line = sock.recv(1024)
        print line
        sock.write("PASS %s\r\n" % ticket)
        line = sock.recv(1024)
        print line
        rand = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        rand = base64.b64encode(rand)
        sock.write("THUMBPRINT %s\r\n" % rand)
        line = sock.recv(1024)
        print line
        sock.write("CONNECT %s mks\r\n" % cfgFile)
        line = sock.recv(1024)
        print line
        sock = ssl.wrap_socket(sock)
        sock.write(rand)
        self.do_proxy(sock)
