import socket
import threading
from datetime import datetime
import json
from hashlib import sha256
import hmac
import base64
import random

def hmac_sha256(data, key):
    key = key.encode('utf-8')
    message = data.encode('utf-8')
    sign = base64.b64encode(hmac.new(key, message, digestmod=sha256).digest())
    sign = str(sign, 'utf-8')
    return sign

class ClientHandler():
    def __init__(self, client, address) -> None:
        self.client = client
        self.client.settimeout(5)
        self.address = address
        self.alive = True
        self.recv_buffer = b""
        self.recv_streams = {}
        self.send_buffers = {}

        self.key = hmac_sha256(f'key{random.random()*100}', 'http11')
        self.recv_thread = threading.Thread(target=self.__recv_loop)
        self.recv_thread.start()
        self.send_thread = threading.Thread(target=self.__send_loop)
        self.send_thread.start()

    def __bad_request_response(self):
        response = {
            'version': "HTTP/2.0", # e.g. "HTTP/1.0"
            'status': "400 Bad Request", # e.g. "200 OK"
            'headers': {'Content-Type': 'text/html'}, # e.g. {content-type: application/json}
            'body': "<html><body><h1>400 Bad Request</h1></body></html>"  
        }
        return response
        
    def __not_found_response(self):
        response = {
            'version': "HTTP/2.0", # e.g. "HTTP/1.0"
            'status': "404 Not Found", # e.g. "200 OK"
            'headers': {'Content-Type': 'text/html'}, # e.g. {content-type: application/json}
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
            if 'id' in params and len(self.recv_streams) > 1:
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

    def __send_headers(self, stream_id, headers, end_stream=False):
        # student implement
        # put header frame into send buffer
        pass

    def __send_body(self, stream_id, body):
        # student implement
        # split the body into data frames
        # put data frames into send buffer
        pass


    def __complete_request(self, stream_id):
        # student implement
        # when you recv a complete stream, call this function
        # handle the request
        pass
        
    def __send_loop(self):
        # student implement
        # send frames in buffer
        # use round robin
        pass


    def __recv_loop(self):
        # student implement
        # recv data and handle the request
        pass

    def close(self):
        self.alive = False
        self.client.close()

class HttpServer():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.host=host
        self.port=port
        self.alive = False

    def __accept_loop(self):
        while self.alive:
            try:
                # Establish a connection with the client
                client, address = self.socket.accept()
                client_handler = ClientHandler(client, address)

                for handler in reversed(self.handler_list):
                    if not handler.alive:
                        self.handler_list.remove(handler)
                self.handler_list.append(client_handler)

            except:
                # catch socket closed
                self.alive = False
                pass


    def run(self):
        if not self.alive:
            # Create a socket object
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to a specific address and port
            self.socket.bind((self.host, self.port))
            
            # Listen for incoming connections
            self.socket.listen(5)
            
            # Create a thread to accept clients
            self.thread = threading.Thread(target=self.__accept_loop)

            self.alive = True
            self.handler_list = []
            self.thread.start()

    def close(self):
        if self.alive:
            self.alive = False
            try:
                self.socket.shutdown(0)
            except:
                pass
            self.socket.close()
            self.thread.join()
            for handler in reversed(self.handler_list):
                if handler.alive:
                    handler.close()

if __name__ == '__main__':
    server = HttpServer()
    server.run()

    while True:
        cmd = input()
        if cmd == 'close' or cmd == 'exit':
            server.close()
            break