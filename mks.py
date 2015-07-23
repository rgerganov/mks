import atexit
import argparse
import getpass
import requests
import sys
import urllib
import urlparse
import webbrowser

from pyVim import connect
from pyVmomi import vim

requests.packages.urllib3.disable_warnings()

def err(msg):
    sys.stderr.write(msg)
    sys.exit(1)

def parse(url):
    p = urlparse.urlparse(url)
    if p.scheme != 'mks':
        err('Invalid URL: only mks scheme is supported')
    if not p.username:
        err('Invalid URL: missing username')
    if not p.hostname:
        err('Invalid URL: missing hostname')
    if not p.path:
        err('Invalid URL: missing path')
    port = p.port if p.port else 443
    pwd = p.password
    if not pwd:
        pwd = getpass.getpass()
    return p.username, pwd, p.hostname, port, p.path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                    help="URL to VM (e.g. 'mks://user:pass@vchost/?name=foo')")
    parser.add_argument("-mhost", help="MKS proxy host (default 'localhost')",
                    default='localhost')
    parser.add_argument("-mport", help="MKS proxy port (default 6090)",
                    type=int, default=6090)
    args = parser.parse_args()

    user, pwd, host, port, path = parse(args.url)
    si = connect.SmartConnect(host=host, user=user, pwd=pwd, port=port)
    atexit.register(connect.Disconnect, si)

    vm = None
    if path.startswith('/?uuid='):
        uuid = path[7:]
        vm = si.content.searchIndex.FindByUuid(None, uuid, True, True)
    elif path.startswith('/?name='):
        name = path[7:]
        content = si.content
        objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine],
                                                          True)
        vmList = objView.view
        for curr_vm in vmList:
            if curr_vm.name == name:
                vm = curr_vm
                break
        objView.Destroy()
    else:
        err('Unsupported VM path: ' + path)

    if not vm:
        err('Cannot find the specified VM')
    ticket = vm.AcquireTicket('mks')
    vm_host = ticket.host if ticket.host else host
    path = '?host={0}&port={1}&ticket={2}&cfgFile={3}&thumbprint={4}'.format(
        vm_host, ticket.port, ticket.ticket, ticket.cfgFile,
        ticket.sslThumbprint)
    base_url = "http://rgerganov.github.io/noVNC/"
    url = "{0}/vnc_auto.html?host={1}&port={2}&path={3}".format(base_url,
                                args.mhost, args.mport, urllib.quote(path))
    webbrowser.open(url)

if __name__ == '__main__':
    main()
