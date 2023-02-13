import socket
import threading
from datetime import datetime
import json
from hashlib import sha256
import hmac
import base64
import random
from Utils import Parser
from QUIC import quic_server
import time

def hmac_sha256(data, key):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    sign = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest())
    sign = str(sign, 'utf-8')
    return sign

class ClientHandler():
    def __init__(self, client, address) -> None:
        self.client = client
        self.address = address
        self.alive = True
        self.key = hmac_sha256(f'key{random.random()*100}', 'http11')
        self.recv_thread =  threading.Thread(target=self.__recv_loop)
        self.recv_thread.start()

    def __bad_request_response(self):
        response = {
            'version': "HTTP/3.0", 
            'status': "400 Bad Request",
            'headers': {'Content-Type': 'text/html'},
            'body': "<html><body><h1>400 Bad Request</h1></body></html>"  
        }
        return response
        
    def __not_found_response(self):
        response = {
            'version': "HTTP/3.0", 
            'status': "404 Not Found",
            'headers': {'Content-Type': 'text/html'},
            'body': "<html><body><h1>404 Not Found</h1></body></html>" 
        }
        return response

    def __do_get(self, request):
        path = request['path']
        params = request['params']
        response = self.__not_found_response()
        if path == "/":
            response['status'] = "200 OK"
            response["headers"] = {'Content-Type': 'text/html'}
            response['body'] = "<html><body>" +\
                                "<h1>HTTP 1.0</h1>" +\
                                "</body></html>"
        elif path == "/get":
            if 'id' in params:
                response['status'] = "200 OK"
                response["headers"] = {'Content-Type': 'application/json'}
                response['body'] = json.dumps({'id': params['id'], 'key':  self.key})
            else:
                response['status'] = "200 OK"
                response["headers"] = {'Content-Type': 'application/json'}
                response['body'] = json.dumps({'id': '', 'key': ''})
        self.__send_response(request, response)

    def __do_post(self, request):
        path = request['path']
        headers = request['headers']
        response = self.__not_found_response()
        print(request)
        if path == "/post":
            if 'content-type' in headers and headers['content-type'] == 'application/json':
                try:
                    post_data = json.loads(request['body'])
                except:
                    post_data = None
            else:
                post_data = None
            if post_data:
                if 'id' in post_data and 'key' in post_data and post_data['key'] ==  self.key:
                    response['status'] = "200 OK"
                    response["headers"] = {'Content-Type': 'application/json'}
                    response['body'] = json.dumps({'success':True})
                    print(post_data['id'], "success")
                else:
                    response['status'] = "200 OK"
                    response["headers"] = {'Content-Type': 'application/json'}
                    response['body'] = json.dumps({'success':False})
                    print(post_data['id'], "fail")
            else:
                response = self.__bad_request_response()
        self.__send_response(request, response)

    def __send_response(self, request, response):
        # student implement
        # send response

        # Log
        print(f"{self.address[0]} - - {datetime.now().strftime('%d/%m/%y %H:%M:%S')} \"{request['method']} {request['path']} {request['version']}\" {response['status']} -")

    def __recv_loop(self):
        # student implement
        # recv data and handle the request
        pass

    def close(self):
        self.alive = False
        self.client.close()

class HttpServer_3_0():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        # Create a socket object
        self.socket = quic_server.QUICServer(host, port)
        self.socket.drop(3)
        self.host = host
        self.port = port
        self.handler = None
        self.alive = False

    def __accept_loop(self):
        while self.alive:
            try:
                if self.handler is None:
                    # Establish a connection with the client
                    self.socket.accept()
                    
                    client_handler = ClientHandler(self.socket, self.socket.client_addr)

                    self.handler = client_handler
                if self.handler and not self.handler.alive:
                    self.handler = None
                    self.socket = quic_server.QUICServer(self.host, self.port)
                    self.socket.drop(3)
                time.sleep(0.01)

            except:
                # catch socket closed
                pass


    def run(self):
        if not self.alive:
            self.alive = True
            self.handler = None
            # Create a thread to accept clients
            self.thread = threading.Thread(target=self.__accept_loop)
            self.thread.start()

    def close(self):
        if self.alive:
            self.alive = False
            self.socket.close()
            self.thread.join()
            if self.handler:
                self.handler.close()

if __name__ == '__main__':
    server = HttpServer_3_0()
    server.run()

    while True:
        cmd = input()
        if cmd == 'close' or cmd == 'exit':
            server.close()
            break