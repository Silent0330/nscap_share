import socket
import json
    
def send_reqeuest(request, host="127.0.0.1", port=8080):
    # student implement
    # send request and return the response
    response = {
        'version': "", # e.g. "HTTP/1.0"
        'status': "", # e.g. "200 OK"
        'headers': {}, # e.g. {content-type: application/json}
        'body': ""  # e.g. "{'id': '123', 'key':'456'}"
    }
    return response
        
if __name__ == '__main__':
    # Send an HTTP GET request to the server
    request = "GET /get?id=123 HTTP/1.0\r\n\r\n"
    response = send_reqeuest(request)
    print(response)
    headers = response['headers']
    body = response['body']

    if 'content-type' in headers and headers['content-type'] == 'application/json':
        try:
            data = json.loads(body)
            if 'id' in data and 'key' in data:
                print(f"Get id={data['id']} key={data['key']}")
            else:
                data = None
        except:
            data = None
    else:
        data = None
    
    if data is None:
        print('Get failed')
        exit()

    # Send an HTTP POST request to the server
    request = f"POST /post HTTP/1.0\r\nContent-Type: application/json\r\n\r\n{json.dumps(data)}"
    response = send_reqeuest(request)
    print(response)
    headers = response['headers']
    body = response['body']
    if 'content-type' in headers and headers['content-type'] == 'application/json':
        try:
            data = json.loads(body)
            if 'success' in data:
                print(f"Post success={data['success']}")
            else:
                data = None
        except:
            data = None
    else:
        data = None
    if not data:
        print('Post failed')