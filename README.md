MKS is the protocol for accessing the console of a virtual machine running on
VMware vSphere. It is pretty much the same as VNC except the authentication
part. This project aims to provide a cross-platform HTML5 client for the MKS
protocol.

Usage
---
Install the project requirements:

    $ pip install -r requirements.txt

Start the MKS proxy. This is websocket proxy which sits between the client and
the hypervisor and handles the authentication part. By default it binds to
localhost:6090

    $ ./mksproxy.py
    Starting MKS proxy on localhost:6090

Run the mks.py script and specify the location of the VM with an URL like this:

    $ ./mks.py 'mks://user:pass@somehost/?name=foo'

This will connect to 'somehost' (either ESX or vCenter), authenticate with
user/pass and then open a web page that displays the VM console of the virtual
machine with the name 'foo'. You can also locate the VM by its UUID like this:

    $ ./mks.py 'mks://user:pass@somehost/?uuid=5965e99a-5f65-454d-bf0d-46ccc57d08db'

How it works
---
We are using a hacked version of the noVNC project which is served from
http://rgerganov.github.io/noVNC. The authd python module is handling the
communication with the authentication daemon running on the hypervisor.

