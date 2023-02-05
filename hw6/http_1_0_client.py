import socket
import json
from Utils import Parser
    
def send_reqeuest(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect(("127.0.0.1", 8080))
    except:
        return None

    try:
        s.sendall(request.encode())
    except:
        s.close()
        return None

    # Receive the server's response
    try:
        response = s.recv(4096).decode()
        version, status, headers, body = Parser.parse_response(response)
    except:
        s.close()
        return None
    s.close()
    return version, status, headers, body
        
        
if __name__ == '__main__':
    # Send an HTTP GET request to the server
    request = "GET /get?id=123 HTTP/1.0\r\n\r\n"
    version, status, headers, body = send_reqeuest(request)

    try:
        data = json.loads(body)
        if 'id' in data and 'key' in data:
            print(f"Get id={data['id']} key={data['key']}")
        else:
            data = None
    except:
        data = None
    
    if not data:
        print('Get failed')

    if data:
        # Send an HTTP POST request to the server
        request = f"POST /post HTTP/1.0\r\nContent-Type: application/json\r\n\r\n{json.dumps(data)}"
        version, status, headers, body = send_reqeuest(request)
        try:
            data = json.loads(body)
            if 'success' in data:
                print(f"Get success={data['success']}")
            else:
                data = None
        except:
            data = None
        if not data:
            print('Post failed')