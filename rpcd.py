#!/usr/bin/env python3
"""
Usage::
    ./rpcd.py [<port>]
"""
from aiorpcx import ClientSession
from server.controller import Controller
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import environ
import asyncio
import json

def handle_json(raw_data):
    result = {
        "jsonrpc": "2.0",
        "params": [],
        "id": None
    }

    error = False
    error_message = ""
    error_code = 0

    try:
        data = json.loads(raw_data)

        if "jsonrpc" not in data or "method" not in data:
            error = True
            error_message = "Invalid Request"
            error_code = -32600 

        if "params" in data:
            if error == False:
                result["params"] = data["params"]

        if "id" in data:
            if type(data["id"]) is str or type(data["id"]) is int:
                result["id"] = data["id"]

        if error == True:
            result["error"] = {
                "code": error_code,
                "message": error_message
            }
        else:
            result["method"] = data["method"]
            result["params"] = data["params"]

    except ValueError:
        result = {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None}

    return result

class RpcServer(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        response = {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}
        data = handle_json(post_data.decode('utf-8'))
        rpc_port = int(environ.get('RPC_PORT', 8000))
        port = int(environ.get('RPC_PORT', 7403))

        print(data)

        if "error" not in data:

            method = data["method"]
            params = data["params"]

            allowed = [
                'blockchain.address.get_balance',
                'blockchain.address.get_history',
                'blockchain.address.get_mempool',
                'blockchain.address.listunspent',
                'blockchain.address.subscribe',
                'blockchain.block.get_chunk',
                'blockchain.block.get_header',
                'blockchain.estimatefee',
                'blockchain.headers.subscribe',
                'blockchain.relayfee',
                'blockchain.scripthash.get_balance',
                'blockchain.scripthash.get_history',
                'blockchain.scripthash.get_mempool',
                'blockchain.scripthash.listunspent',
                'blockchain.scripthash.subscribe',
                'blockchain.transaction.broadcast',
                'blockchain.transaction.get',
                'blockchain.transaction.get_merkle',
                'getinfo'
            ]

            async def send_request():
                if method == "getinfo":
                    async with ClientSession('localhost', rpc_port) as session:
                        response = await session.send_request(method, params, timeout=15)

                else:
                    async with ClientSession('localhost', port) as session:
                        response = await session.send_request(method, params, timeout=15)

                self._set_response()
                self.wfile.write(json.dumps(response, indent=4, sort_keys=True).encode('utf-8'))

            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(send_request())
            except OSError:
                print('cannot connect - is ElectrumX catching up, not running, or '
                      f'is {port} the wrong RPC port?')
            except Exception as e:
                print(f'error making request: {e}')

        else:
            self._set_response()
            self.wfile.write(json.dumps(response, indent=4, sort_keys=True).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=RpcServer, port=4321):
    server_address = ('', port)
    rpcd = server_class(server_address, handler_class)
    print('Starting rpcd on port {}...\n'.format(port))

    try:
        rpcd.serve_forever()
    except KeyboardInterrupt:
        pass

    rpcd.server_close()
    print('Stopping rpcd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
