import atexit
import argparse
import requests
import urllib
import webbrowser

from pyVim import connect

requests.packages.urllib3.disable_warnings()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="vSphere host", required=True)
    parser.add_argument("-port", help="vSphere port (default 443)",
                        type=int, default=443)
    parser.add_argument("-mhost", help="MKS proxy host (default 'localhost')",
                        default='localhost')
    parser.add_argument("-mport", help="MKS proxy port (default 6090)",
                        type=int, default=6090)
    parser.add_argument("-user", help="vSphere user", required=True)
    parser.add_argument("-pwd", help="vSphere password", required=True)
    parser.add_argument("-uuid", help="VM uuid", required=True)
    args = parser.parse_args()

    si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.pwd,
                              port=args.port)
    atexit.register(connect.Disconnect, si)
    vm = si.content.searchIndex.FindByUuid(None, args.uuid, True, True)
    ticket = vm.AcquireTicket('mks')

    vm_host = ticket.host if ticket.host else args.host

    path = '?host={0}&port={1}&ticket={2}&cfgFile={3}&thumbprint={4}'.format(
        vm_host, ticket.port, ticket.ticket, ticket.cfgFile,
        ticket.sslThumbprint)
    base_url = "http://rgerganov.github.io/noVNC/"
    url = "{0}/vnc_auto.html?host={1}&port={2}&path={3}".format(base_url,
                                args.mhost, args.mport, urllib.quote(path))
    webbrowser.open(url)
