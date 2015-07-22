import argparse
import authd
import websockify

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-host", help="MKS proxy host (default 'localhost')",
                        default='localhost')
    parser.add_argument("-port", help="MKS proxy port (default 6090)",
                        type=int, default=6090)
    parser.add_argument("--web", help="web location")
    args = parser.parse_args()

    print('Starting MKS proxy on {0}:{1}'.format(args.host, args.port))
    websockify.WebSocketProxy(
        listen_host=args.host,
        listen_port=args.port,
        verbose=True,
        web=args.web,
        file_only=True,
        RequestHandlerClass=authd.AuthdRequestHandler
    ).start_server()
