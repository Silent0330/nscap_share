import socket
import threading

class HTTPClient:
    def __init__(self) -> None:
        self.connecting = False

    def __get_next_stream_id(self):
        stream_id = self.next_stream_id
        self.next_stream_id += 2
        return stream_id
    
    def connect(self, host="127.0.0.1", port=8080):
        if not self.connecting:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            try:
                self.socket.connect((host, port))
                
                self.connecting = True
                self.recv_buffer = b""
                self.recv_streams = {}
                self.send_buffers = {}
                self.next_stream_id = 1
                self.recv_thread = threading.Thread(target=self.__recv_loop)
                self.recv_thread.start()
                self.send_thread = threading.Thread(target=self.__send_loop)
                self.send_thread.start()
            except:
                self.connecting = False
                self.socket.close()

    def __complete_stream(self, stream_id):
        if stream_id in self.recv_streams:
            self.recv_streams[stream_id]['complete'] = True

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

    def __send_loop(self):
        # student implement
        # send frames in buffer
        # use round robin
        pass

    def __recv_loop(self):
        # student implement
        # recv data and handle the request
        pass

    def __send_headers(self, stream_id, headers, end_stream=False):
        # student implement
        # put header frame into send buffer
        pass

    def __send_body(self, stream_id, body):
        # student implement
        # split the body into data frames
        # put data frames into send buffer
        pass
        
    def send_reqeuest(self, request):
        # student implement
        # send request
        pass
        
    def close(self):
        self.connecting = False
        self.socket.close()
       
def demo():
    client = HTTPClient()
    client.connect()

    headers = [
        (':method', 'GET'),
        (':path', '/get?id=123'),
        (':scheme', 'http'),
        (':authority', '127.0.0.1:8080')
    ]
    body = b'0' * 10
    request = {
        'headers': headers,
        'body': body
    }

    stream_id_1 = client.send_reqeuest(request)
    stream_id_2 = client.send_reqeuest(request)
    response = client.wait_for_response(stream_id_1)
    if not response:
        exit()
    data = response['body']
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
    body = data.encode()
    request = {
        'headers': headers,
        'body': body
    }
    stream_id_3 = client.send_reqeuest(request)
    response = client.wait_for_response(stream_id_3)
    print(stream_id_3, response)

    client.close()