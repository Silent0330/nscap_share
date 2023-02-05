# nscap_hw6
ppt : 
https://docs.google.com/presentation/d/1KqHFxjEP76IZ1toVVzJM_oSdO7faguRc/edit?usp=sharing&ouid=112064783971576677983&rtpof=true&sd=true 
## Problem
Design and implement a pair of web client program and web server program that support the HTTP 1.0, HTTP 1.1, and HTTP 2.0 protocols, respectively.
## Test
### Submission
{student_id}_hw6.zip
├──http_1_0_client.py
├──http_1_0_server.py
├──http_1_1_client.py
├──http_1_1_server.py
├──http_2_0_client.py
└──http_2_0_server.py
### Method
* TA's client connect to student's server
* student's client connect to TA's server
### HTTP 1.0
* Client send a GET request `/get` with query `id=<studendid>`.
* Server response in json format `{id=<sutdentid>,key=<key>}`. Hints: Key is a hash value of id, you can use any hash function in your server.
* Client send a POST reqeust `/post` with json format body `{id=<sutdentid>,key=<key>}`.
* Server response in json format `{success=true}` or `{success=false}` depending on key.
### HTTP 1.1
* Client send a GET request `/get` with query `id=<studendid>`.
* Server response in json format `{id=<sutdentid>,key=<key>}`. Hints: Key will be different in each connection.
* Client send a POST reqeust `/post` with json format body `{id=<sutdentid>,key=<key>}`.
* Server response in json format `{success=true}` or `{success=false}` depending on key.
### HTTP 2.0
* Client send two header frames of GET request `/get` with query `id=<studendid>`.
* Client send two body frames for these streams.
* Server response in json format `{id=<sutdentid>,key=<key>}` for each stream. Hints: Only the first stream contains the actual value.
* Client send a POST reqeust `/post` with json format body `{id=<sutdentid>,key=<key>}`.
* Server response in json format `{success=true}` or `{success=false}` depending on key.
## Tips
### request format
* `<method> <URI> <HTTP-version>\r\n<headers>\r\n<body>`
* Each header in `<headers>` is `<key>:<value>\r\n`.
### response format
* `<HTTP-version> <status message>\r\n<headers>\r\n<body>`
* Each header in `<headers>` is `<key>:<value>\r\n`
### http 1.0
* Each connection accepts one request.
### http 1.1
* Each connection keeps alive for a while.
### http 2.0
* Each connection keeps alive for a while.
* Request is splited into headers frame and data frames
* Use h2 libary to encode and decode them.
* If data larger than threshold, it will be divided into multiple data frames.
* Receive an endstream event to complete a stream.
* Headers shold be lower case.
* Default headers example
    ```
    (':method', 'GET'),
    (':path', '/get'),
    (':version', 'HTTP/2.0'),
    (':scheme', 'http'),
    ```
### h2
* initial
``` python
    config = h2.config.H2Configuration(client_side=True, header_encoding='utf-8’) 
    # Create an h2 connection object
    h2conn = h2.connection.H2Connection(config=config) 
    # Initiate the connection
    h2conn.initiate_connection()
    socket.sendall(self.h2conn.data_to_send())
```
* send headers frame
``` python
    headers = [(':method', 'GET'),(':path', '/get?id=123'),(':scheme', 'http'),(':authority', '127.0.0.1:8080')]
    h2conn.send_headers(stream_id, headers, end_stream=end_stream)
```
* send data frame
``` python
    chunk_size = min(len(body),h2conn.max_outbound_frame_size)
    while len(body) > chunk_size:
        h2conn.send_data(stream_id, body[:chunk_size])
        body = body[chunk_size:]
    h2conn.send_data(stream_id, body, end_stream=end_stream)
    socket.sendall(self.h2conn.data_to_send())
```
* recv h2 events
``` python
    if isinstance(event, h2.events.ResponseReceived):
        self.streams[event.stream_id]['headers'] = event.headers
    elif isinstance(event, h2.events.DataReceived):
        # update flow control so the server doesn't starve us
        self.h2conn.acknowledge_received_data(event.flow_controlled_length, event.stream_id)
        # more response body data received
        self.streams[event.stream_id]['body'] += event.data
    elif isinstance(event, h2.events.StreamEnded):
        # request or response complete
        self.__complete_stream(event.stream_id)
```

