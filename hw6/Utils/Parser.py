def parse_header(data):
    # Split the request into a list of strings
    lines = data.split('\r\n')
    # Initialize an empty dictionary to store the headers
    headers = {}
    # Iterate through the lines
    for line in lines:
        # Skip empty lines
        if line == '':
            break
        # Split the line into a key-value pair
        index = line.find("=")
        if index != -1 and index+2<len(line):
            key, value = line[:index].strip(), line[index+1:].strip()
            headers[key.lower()] = value
    return headers

def parse_resource(resource):
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
    return path, params

def parse_response(response):
    # Split the request into a list of strings
    lines = response.split('\r\n')

    # Split the method, resource and version
    request_list = lines[0].split()
    
    # Extract method and requested resource
    version = request_list[0]
    status = request_list[1]

    # Initialize an empty dictionary to store the headers
    headers = {}

    # Iterate through the lines
    for line in lines[1:]:
        # Skip empty lines
        if line == '':
            break
        # Split the line into a key-value pair
        line = line.split(':')
        if (len(line) == 2):
            key, value = line
            headers[key.strip().lower()] = value.strip()

    # Extract the body (if any)
    body = ""
    if "\r\n\r\n" in response:
        body = response.split("\r\n\r\n")[1]
    return version, status, headers, body

def parse_reqeust(request):
    # Split the request into a list of strings
    lines = request.split('\r\n')

    # Split the method, resource and version
    request_list = lines[0].split()
    
    # Extract method and requested resource
    method = request_list[0]
    resource = request_list[1]
    version = request_list[2]

    # Initialize an empty dictionary to store the headers
    headers = {}

    path, params = parse_resource(resource)

    # Iterate through the lines
    for line in lines[1:]:
        # Skip empty lines
        if line == '':
            break
        # Split the line into a key-value pair
        line = line.split(':')
        if (len(line) == 2):
            key, value = line
            headers[key.strip().lower()] = value.strip()

    # Extract the body (if any)
    body = ""
    if "\r\n\r\n" in request:
        body = request.split("\r\n\r\n")[1]

    return method, path, params, version, headers, body
