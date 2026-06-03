from http.server import ThreadingHTTPServer, HTTPServer
from handler import MinesweeperRequestHandler
import argparse

# Arguments
parser = argparse.ArgumentParser(description='Minesweeper HTTP API')
parser.add_argument('--no-threading', help='do not enable multithreading',
    action='store_true')
parser.add_argument('-p', '--port', type=int, help="port to listen on",
    default=8080)
parser.add_argument('-i', '--ip', type=str, help="host IP to listen on",
    default='')
args = parser.parse_args()

# Start server
server_class = HTTPServer if args.no_threading else ThreadingHTTPServer
httpd = server_class((args.ip, args.port), MinesweeperRequestHandler)
httpd.serve_forever()
