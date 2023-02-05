import socket
import json
from Utils import Parser

class HTTPClient:
    def __init__(self, host="127.0.0.1", port=8080) -> None:
        self.connecting = False
        self.host=host
        self.port=port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send_reqeuest(self, request):
        if not self.connecting:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            try:
                self.socket.connect(("127.0.0.1", 8080))
                self.connecting = True
            except:
                return None

        try:
            print(request.encode())
            self.socket.sendall(request.encode())
        except:
            self.connecting = True
            self.socket.close()
            return None

        # Receive the server's response
        try:
            response = self.socket.recv(4096).decode()
            version, status, headers, body = Parser.parse_response(response)
        except:
            self.connecting = True
            self.socket.close()
            return None
        
        return version, status, headers, body
        
        



if __name__ == '__main__':
    client = HTTPClient()

    response = client.send_reqeuest("GET /get?id=123 HTTP/1.1\r\n\r\n")
    if not response:
        print('GET failed')
        exit()
    version, status, headers, body = response
    
    try:
        data = json.loads(body)
        if 'id' in data and 'key' in data:
            print(f"get id={data['id']} key={data['key']}")
        else:
            data = None
    except:
        data = None
    
    if not data:
        print('GET failed')

    if data:
        response = client.send_reqeuest(f"POST /post HTTP/1.1\r\nContent-Type: application/json\r\n\r\n{json.dumps(data)}")
        if not response:
            print('POST failed')
            exit()
        version, status, headers, body = response
        try:
            data = json.loads(body)
            if 'success' in data:
                print(f"Get success={data['success']}")
            else:
                data = None
        except:
            data = None
        if not data:
            print('POST failed')