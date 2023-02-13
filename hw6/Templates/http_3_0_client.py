import socket
import threading
import json
import time
from Utils import Frame
from Utils import Parser
from QUIC import quic_client

class HTTPClient:
    def __init__(self) -> None:
        self.connecting = False

    def __get_next_stream_id(self):
        stream_id = self.next_stream_id
        self.next_stream_id += 2
        return stream_id
    
    def connect(self, host="127.0.0.1", port=8080):
        if not self.connecting:
            self.socket = quic_client.QUICClient()
            try:
                self.socket.connect((host, port))
                
                self.connecting = True
                self.recv_buffer = b""
                self.recv_streams = {}
                self.next_stream_id = 1
                self.recv_thread = threading.Thread(target=self.__recv_loop)
                self.recv_thread.start()
            except:
                self.connecting = False
                self.socket.close()

    def wait_for_response(self, stream_id):
        response = {
            'version': "HTTP/2.0", # e.g. "HTTP/1.0"
            'status': "", # e.g. "200 OK"
            'headers': {}, # e.g. {content-type: application/json}
            'body': ""  # e.g. "{'id': params['id'], 'key': hmac_sha256(params['id'], 'http10')}"
        }
        # student implement
        # use a loop to wait the stream complete and return response
        # You may need to use counter and time.sleep() to wait about 3s. If time out, return None.
        return None

    def __recv_loop(self):
        # student implement
        # recv data and handle the request
        pass
        
    def send_reqeuest(self, request):
        # student implement
        # send request and return the response
        pass

    def close(self):
        self.connecting = False
        self.socket.close()
        


if __name__ == '__main__':
    client = HTTPClient()
    client.connect()

    request = "GET /get?id=123 HTTP/3.0\r\n\r\n"

    stream_id_1 = client.send_reqeuest(request)
    stream_id_2 = client.send_reqeuest(request)
    response = client.wait_for_response(stream_id_1)
    data = json.loads(response['body'])
    print(stream_id_1, response)
    response = client.wait_for_response(stream_id_2)
    print(stream_id_2, response)
    headers = [
        (':method', 'POST'),
        (':path', '/post'),
        (':scheme', 'http'),
        (':authority', '127.0.0.1:8080'),
        ('content-type', 'application/json')
    ]
    request = f"POST /post HTTP/3.0\r\nContent-Type: application/json\r\n\r\n{json.dumps(data)}"
    stream_id_3 = client.send_reqeuest(request)
    response = client.wait_for_response(stream_id_3)
    print(stream_id_3, response)

    client.close()