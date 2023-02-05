import socket
import threading
from datetime import datetime
import json
from hashlib import sha256
import hmac
import base64
from Utils import Parser

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
        self.thread =  threading.Thread(target=self.__handle_loop)
        self.thread.start()

    def __handle_loop(self):
        try:
            # Recv request
            request = self.client.recv(4096).decode()

            # check connection
            if request == "":
                self.alive = False
                self.client.close()
                return

            # parse request
            method, path, params, version, headers, body = Parser.parse_reqeust(request)
            status = 200
            # Check the method and path
            if method == "GET":
                if path == "/":
                    response = "HTTP/1.0 200 OK\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += "<html><body>" +\
                                "<h1>HTTP 1.0</h1>" +\
                                "</body></html>"
                elif path == "/get":
                    if 'id' in params:
                        response = "HTTP/1.0 200 OK\r\n"
                        response += "Content-Type: application/json\r\n\r\n"
                        response += json.dumps({'id': params['id'], 'key': hmac_sha256(params['id'], 'http10')})
                    else:
                        response = "HTTP/1.0 200 OK\r\n"
                        response += "Content-Type: application/json\r\n\r\n"
                        response += json.dumps({'id': '', 'key': ''})
                else:
                    status = 404
                    response = "HTTP/1.0 404 Not Found\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += "<html><body><h1>404 Not Found</h1></body></html>"
            elif method == "POST":
                if path == "/post":
                    if 'content-type' in headers and headers['content-type'] == 'application/json':
                        try:
                            data = json.loads(body)
                        except:
                            data = None
                    else:
                        data = None
                    if data:
                        if 'id' in data and 'key' in data and data['key'] == hmac_sha256(data['id'], 'http10'):
                            response = "HTTP/1.0 200 OK\r\n"
                            response += "Content-Type: application/json\r\n\r\n"
                            response += json.dumps({'success':True})
                            print(data['id'], "success")
                        else:
                            response = "HTTP/1.0 200 OK\r\n"
                            response += "Content-Type: application/json\r\n\r\n"
                            response += json.dumps({'success':False})
                            print(data['id'], "fail")
                    else:
                        status = 400
                        response = "HTTP/1.0 400 Bad Request\r\n"
                        response += "Content-Type: text/html\r\n\r\n"
                        response += "<html><body><h1>400 Bad Request</h1></body></html>"
                else:
                    status = 404
                    response = "HTTP/1.0 404 Not Found\r\n"
                    response += "Content-Type: text/html\r\n\r\n"
                    response += "<html><body><h1>404 Not Found</h1></body></html>"
            else:
                status = 400
                response = "HTTP/1.0 400 Bad Request\r\n"
                response += "Content-Type: text/html\r\n\r\n"
                response += "<html><body><h1>400 Bad Request</h1></body></html>"

            # Send the response to the client
            self.client.sendall(response.encode())

            # Log
            print(f'{self.address[0]} - - {datetime.now().strftime("%d/%m/%y %H:%M:%S")} "{method} {path} {version}" {status} -')

            # Close the connection with the client
            self.client.close()
            pass
        except:
            self.alive = False
            pass

    def close(self):
        self.alive = False
        self.client.close()

class HttpServer_1_0():
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

            except:
                # catch socket closed
                pass


    def run(self):
        if not self.alive:
            self.alive = True
            self.thread.start()

    def close(self):
        self.alive = False
        self.socket.close()
        self.thread.join()

if __name__ == '__main__':
    server = HttpServer_1_0()
    server.run()

    while True:
        cmd = input()
        if cmd == 'close' or cmd == 'exit':
            server.close()
            break