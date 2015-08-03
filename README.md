MKS is the protocol for accessing the console of a virtual machine running on
VMware vSphere. It is pretty much the same as VNC except the authentication
part. This project aims to provide a cross-platform HTML5 client for the MKS
protocol.

Installation
---
Install the project requirements (preferably into a virtualenv) :

    $ pip install -r requirements.txt

Usage with vSphere 5.x
---
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

Usage with vSphere 6.0
---
Same as vSphere 5.x but you don't need to run `mksproxy.py`. Just run `mks.py`

How it works
---
If vSphere 5.x is detected, we use a modified version of noVNC and proxy server
which creates websockets and talks to authd. Starting from vSphere 6, websocket
consoles are supported out of the box, so we use the stock version of noVNC in
this case. Both versions are served from http(s)://rgerganov.github.io/noVNC

Security notice
---
For simplicity's sake this code doesn't handle security "the right way".
Don't use it in production.

