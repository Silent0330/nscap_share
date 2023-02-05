import socket
import threading
from datetime import datetime
import json
from hashlib import sha256
import hmac
import base64
import random
from Utils import Frame
from Utils import Parser
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

    def __send_headers(self, stream_id, headers, end_stream=False):
        hdr = ""
        for header in headers:
            hdr += f"{header[0]} = {header[1]}\r\n"
        frame = Frame.create_headers_frame(stream_id, hdr.encode(), end_stream)
        self.send_buffers[stream_id] = [frame]

    def __send_body(self, stream_id, body):
        chunk_size = Frame.Frame.max_payload_size
        while len(body) > chunk_size:
            frame = Frame.create_data_frame(stream_id, body[:chunk_size])
            body = body[chunk_size:]
            self.send_buffers[stream_id].append(frame) 
        frame = Frame.create_data_frame(stream_id, body, end_stream=True)
        self.send_buffers[stream_id].append(frame) 

    def __complete_request(self, stream_id):
        try:
            stream = self.recv_streams[stream_id]
            headers = stream['headers']
            body = stream['body'].decode('utf-8')
            method = headers[':method']
            scheme = headers[':scheme']
            resource = headers[':path']
            # Split resource into path and parameters
            resource = resource.split('?')
            if len(resource) == 2:
                path, parameters = resource
            else:
                path = resource[0]
                parameters = ''
            
            # Split the parameters into list
            parameters = parameters.split('&')

            # Initialize an empty dictionary to store the params
            params = {}
            
            # Iterate through the parameters
            for para in parameters:
                # Split the para into a key-value pair
                para = para.split('=')
                if (len(para) == 2):
                    key, value = para
                    params[key] = value
        except:
            if stream_id in self.recv_streams:
                del self.recv_streams[stream_id]
            return
        # Check the method and path
        status = 200
        if method == "GET":
            if path == "/":
                data = "<html><body>" +\
                        "<h1>HTTP 1.0</h1>" +\
                        "</body></html>"
                data =  data.encode("utf8")
                headers = [
                    (':status', '200'),
                    ('content-type', 'text/html'),
                    ('content-length', str(len(data))),
                ]
                self.__send_headers(stream_id, headers)
                self.__send_body(stream_id, data)
            elif path == "/get":
                if 'id' in params and len(self.recv_streams) > 1:
                    data = json.dumps({'id': params['id'], 'key': self.key})
                    data =  data.encode("utf8")
                    headers = [
                        (':status', '200'),
                        ('content-type', 'application/json'),
                        ('content-length', str(len(data))),
                    ]
                    self.__send_headers(stream_id, headers)
                    self.__send_body(stream_id, data)
                else:
                    data = json.dumps({'id': '', 'key': ''})
                    data =  data.encode("utf8")
                    headers = [
                        (':status', '200'),
                        ('content-type', 'application/json'),
                        ('content-length', str(len(data))),
                    ]
                    self.__send_headers(stream_id, headers)
                    self.__send_body(stream_id, data)
            else:
                status = 404
                data = "<html><body><h1>404 Not Found</h1></body></html>"
                data =  data.encode("utf8")
                headers = [
                    (':status', '404'),
                    ('content-type', 'text/html'),
                    ('content-length', str(len(data))),
                ]
                self.__send_headers(stream_id, headers)
                self.__send_body(stream_id, data)
        elif method == "POST":
            if path == "/post":
                if 'content-type' in headers and headers['content-type'] == 'application/json':
                    try:
                        post_data = json.loads(body)
                    except:
                        post_data = None
                else:
                    post_data = None
                if post_data:
                    if 'id' in post_data and 'key' in post_data and post_data['key'] == self.key:
                        data = json.dumps({'msg':'success'})
                        data =  data.encode("utf8")
                        headers = [
                            (':status', '200'),
                            ('content-type', 'application/json'),
                            ('content-length', str(len(data))),
                        ]
                        self.__send_headers(stream_id, headers)
                        self.__send_body(stream_id, data)
                        print(post_data['id'], "success")
                    else:
                        data = json.dumps({'msg':'fail'})
                        data =  data.encode("utf8")
                        headers = [
                            (':status', '200'),
                            ('content-type', 'application/json'),
                            ('content-length', str(len(data))),
                        ]
                        self.__send_headers(stream_id, headers)
                        self.__send_body(stream_id, data)
                        print(post_data['id'], "fail")
                else:
                    status = 400
                    data = "<html><body><h1>400 Bad Request</h1></body></html>"
                    data =  data.encode("utf8")
                    headers = [
                        (':status', '400'),
                        ('content-type', 'application/json'),
                        ('content-length', str(len(data))),
                    ]
                    self.__send_headers(stream_id, headers)
                    self.__send_body(stream_id, data)
            else:
                status = 404
                data = "<html><body><h1>404 Not Found</h1></body></html>"
                data =  data.encode("utf8")
                headers = [
                    (':status', '404'),
                    ('content-type', 'application/json'),
                    ('content-length', str(len(data))),
                ]
                self.__send_headers(stream_id, headers)
                self.__send_body(stream_id, data)
        else:
            status = 400
            data = "<html><body><h1>400 Bad Request</h1></body></html>"
            data =  data.encode("utf8")
            headers = [
                (':status', '400'),
                ('content-type', 'application/json'),
                ('content-length', str(len(data))),
            ]
            self.__send_headers(stream_id, headers)
            self.__send_body(stream_id, data)

        # Log
        print(f'{self.address[0]} - - {datetime.now().strftime("%d/%m/%y %H:%M:%S")} "{method} {path}" {status} -')
        del self.recv_streams[stream_id]
        
    def __send_loop(self):
        while self.alive:
            try:
                end_streams = []
                keys = list(self.send_buffers.keys())
                for key in keys:
                    if len(self.send_buffers[key]) > 0:
                        frame = self.send_buffers[key].pop(0)
                        self.client.sendall(frame.to_bytes())
                        if frame.flags == 1:
                            end_streams.append(key)
                for key in end_streams:
                    del self.send_buffers[key]
            except:
                self.alive = False
                self.client.close()
                break


    def __recv_loop(self):
        while self.alive:
            try:
                # Recv request
                recv_bytes = self.client.recv(8192)

                # check connection
                if not recv_bytes:
                    self.alive = False
                    self.client.close()
                    break

                recv_bytes = self.recv_buffer + recv_bytes

                # parse request
                frames, remian_bytes = Frame.bytes_to_frames(recv_bytes)
                self.recv_buffer = remian_bytes
                for frame in frames:
                    if frame.type == 0: # data
                        self.recv_streams[frame.stream_id]['body'] += frame.payload
                    elif frame.type == 1: # header
                        headers = Parser.parse_header(frame.payload.decode())
                        self.recv_streams[frame.stream_id] = {
                            'headers': headers,
                            'body': b''
                        }
                    if frame.flags == 1:
                        self.__complete_request(frame.stream_id)
            except:
                self.alive = False
                self.client.close()
                break

    def close(self):
        self.alive = False
        self.client.close()

class HttpServer_2_0():
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        # Create a socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific address and port
        self.socket.bind((host, port))
        
        # Listen for incoming connections
        self.socket.listen(5)
        
        # Create a thread to accept clients
        self.thread = threading.Thread(target=self.__accept_loop)

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
            self.alive = True
            self.handler_list = []
            self.thread.start()

    def close(self):
        self.alive = False
        self.socket.close()
        self.thread.join()
        for handler in reversed(self.handler_list):
            if handler.alive:
                handler.close()

if __name__ == '__main__':
    server = HttpServer_2_0()
    server.run()

    while True:
        cmd = input()
        if cmd == 'close' or cmd == 'exit':
            server.close()
            break