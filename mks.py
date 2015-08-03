#!/usr/bin/env python
# Copyright (c) 2015 Radoslav Gerganov
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import atexit
import argparse
import getpass
import requests
import ssl
import sys
import urllib
import urlparse
import webbrowser

from pyVim import connect
from pyVmomi import vim

requests.packages.urllib3.disable_warnings()

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

def err(msg):
    sys.stderr.write(msg + '\n')
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
    query = p.query
    if not query:
        if p.path.startswith("/?"):
            # http://bugs.python.org/issue9374
            query = p.path[2:]
        else:
            err('Invalid URL: missing query')
    port = p.port if p.port else 443
    pwd = p.password
    if not pwd:
        pwd = getpass.getpass()
    return p.username, pwd, p.hostname, port, query

def vsphere_url(vm, host, args):
    # Generates console URL for vSphere versions prior 6.0
    ticket = vm.AcquireTicket('mks')
    vm_host = ticket.host if ticket.host else host
    path = '?host={0}&port={1}&ticket={2}&cfgFile={3}&thumbprint={4}'.format(
        vm_host, ticket.port, ticket.ticket, ticket.cfgFile,
        ticket.sslThumbprint)
    base_url = "http://rgerganov.github.io/noVNC/5"
    url = "{0}/vnc_auto.html?host={1}&port={2}&path={3}".format(base_url,
                                args.mhost, args.mport, urllib.quote(path))
    return url

def vsphere6_url(vm, host):
    # Generates console URL for vSphere 6
    ticket = vm.AcquireTicket('webmks')
    vm_host = ticket.host if ticket.host else host
    path = "ticket/" + ticket.ticket
    base_url = "https://rgerganov.github.io/noVNC/6"
    url = "{0}/vnc_auto.html?host={1}&path={2}".format(base_url, vm_host, urllib.quote(path))
    return url

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url",
                    help="URL to VM (e.g. 'mks://user:pass@vchost/?name=foo')")
    parser.add_argument("-mhost", help="MKS proxy host (default 'localhost')",
                    default='localhost')
    parser.add_argument("-mport", help="MKS proxy port (default 6090)",
                    type=int, default=6090)
    args = parser.parse_args()

    user, pwd, host, port, query = parse(args.url)
    si = connect.SmartConnect(host=host, user=user, pwd=pwd, port=port)
    atexit.register(connect.Disconnect, si)

    vm = None
    if query.startswith('uuid='):
        uuid = query[5:]
        vm = si.content.searchIndex.FindByUuid(None, uuid, True, True)
    elif query.startswith('name='):
        name = query[5:]
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
        err('Unsupported VM identifier: ' + query)

    if not vm:
        err('Cannot find the specified VM')
    if si.content.about.version.startswith("6"):
        url = vsphere6_url(vm, host)
    else:
        url = vsphere_url(vm, host, args)
    webbrowser.open(url)

if __name__ == '__main__':
    main()
