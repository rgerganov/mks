import urlparse
import websockify
import socket
import ssl
import base64
import hashlib
import string
import random

VMAD_OK = 200
VMAD_WELCOME = 220
VMAD_LOGINOK = 230
VMAD_NEEDPASSWD = 331
VMAD_USER_CMD = "USER"
VMAD_PASS_CMD = "PASS"
VMAD_THUMB_CMD = "THUMBPRINT"
VMAD_CONNECT_CMD = "CONNECT"


def expect(sock, code):
    line = sock.recv(1024)
    recv_code = int(line.split()[0])
    if code != recv_code:
        raise Exception('Expected %d but received %d' % (code, recv_code))


def handshake(host, port, ticket, cfg_file, thumbprint):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    expect(sock, VMAD_WELCOME)
    sock = ssl.wrap_socket(sock)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    cert = sock.getpeercert(binary_form=True)
    h = hashlib.sha1()
    h.update(cert)
    if thumbprint != h.hexdigest():
        raise Exception("Server thumbprint doesn't match")
    sock.write("%s %s\r\n" % (VMAD_USER_CMD, ticket))
    expect(sock, VMAD_NEEDPASSWD)
    sock.write("%s %s\r\n" % (VMAD_PASS_CMD, ticket))
    expect(sock, VMAD_LOGINOK)
    alphabet = string.ascii_letters + string.digits
    rand = ''.join(random.SystemRandom().choice(alphabet) for _ in range(12))
    rand = base64.b64encode(rand)
    sock.write("%s %s\r\n" % (VMAD_THUMB_CMD, rand))
    expect(sock, VMAD_OK)
    sock.write("%s %s mks\r\n" % (VMAD_CONNECT_CMD, cfg_file))
    expect(sock, VMAD_OK)
    sock = ssl.wrap_socket(sock)
    sock.write(rand)
    return sock

class AuthdRequestHandler(websockify.ProxyRequestHandler):

    def new_websocket_client(self):
        parse = urlparse.urlparse(self.path)
        query = parse.query
        args = urlparse.parse_qs(query)
        host = args.get("host", [""]).pop()
        port = args.get("port", [""]).pop()
        port = int(port)
        ticket = args.get("ticket", [""]).pop()
        cfg_file = args.get("cfgFile", [""]).pop()
        thumbprint = args.get("thumbprint", [""]).pop()
        thumbprint = thumbprint.replace(':', '').lower()

        tsock = handshake(host, port, ticket, cfg_file, thumbprint)
        self.do_proxy(tsock)
