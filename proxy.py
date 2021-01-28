import sys, os, time, socket, select


def add_cache_box(webpage):
    """
    Adds a notification box in html recieved from the webpage indicating
    if the webpage is fresh or cached.
    """
    index = webpage.find("<body>")


def get_header_val(name, header):
    """
    parses HTML headers for the value of given header name
    :param name: name of the header
    :param header: HTML header
    :return: the value of the specified header
    """
    index = header.find(name)
    if index == -1:
        return -1
    index += len(name)+1
    num = header[index:].split(b"\r\n", 1)
    return num[0].strip()


def contact_webserver(webaddress, request, client_socket):
    """
    Creates a client to request data from given web address using the
    request header
    :param client_socket: socket of the client connection
                           (used index into socket_pair dictionary)
    :param webaddress: The address of the web server
    :param request: The request header to send to the web server
    :return: the webpage/file sent by the web server
    """
    webpage = b""
    sock = None
    try:
        # check if client already has a connection
        if client_socket in socket_pairs.keys() and \
                webaddress == socket_pairs[client_socket]["host"]:
            # print("used old socket for web server")
            print("using old socket")
            sock = socket_pairs[client_socket]["sock"]
        else:
            # print("made new socket to connect to webserver")
            if client_socket in socket_pairs.keys() and \
                    webaddress != socket_pairs[client_socket]["host"]:
                print("closing old web server socket")
                socket_pairs[client_socket]["sock"].close()
            print("creating new webserver socket")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = (webaddress, 80)
            sock.connect(address)
            socket_pairs[client_socket] = {"sock": sock, "host": webaddress}

        sock.sendall(request)

        data = sock.recv(1024)
        encoding = get_header_val(b"Transfer-Encoding", data)

        if encoding == b"chunked":  # handle chunked transfer encoding
            webpage += data
            while True:
                data = sock.recv(1024)
                if data:
                    webpage += data
                    if webpage[-4::] == b"\r\n\r\n":
                        break
                else:
                    break

        else:  # handle other transfer encoding that have content length on them
            num = get_header_val(b"Content-Length", data)
            if num == -1:
                return data

            content_len = int(num)
            content_index = data.find(b"\r\n\r\n") + 4
            curr_len = len(data[content_index:])
            webpage += data
            while curr_len < content_len:
                data = sock.recv(1024)
                webpage += data
                curr_len += len(data)

    except socket.error:
        print("Unable to connect to web server")
        sock.close()
        socket_pairs.pop(client_socket)

    return webpage


def modify_header(request, sock):

    # get web address
    temp = request.split(b" ", 2)
    address_parts = temp[1].split(b"/", 2)

    # change GET path
    path = b""
    if address_parts[1].count(b'.') > 1:  # handle relative paths
        host = address_parts[1]  # since address starts with / [1] is the domain
        if len(address_parts) < 3 or address_parts[2] == '':
            path = b" / "
            # if the address is "/www.example.com" then this only has 2 parts
        else:
            path = b" /" + address_parts[2] + b" "
        request = temp[0] + path + temp[2]
    else:
        host = socket_pairs[sock]["host"]

    # host = address_parts[1]  # since address starts with / [1] is the domain
    # # change GET path
    # path = b""
    # if len(address_parts) < 3:
    #     path = b" / "
    #     # if the address is "/www.example.com" then this only has 2 parts
    # else:
    #     path = b" /" + address_parts[2] + b" "
    # request = temp[0] + path + temp[2]

    # change HOST header with domain address
    start_index = request.find(b"Host:")
    if start_index != -1:
        request = request[:start_index] + b"Host: " + host + b" \r\n"\
                  + request[start_index:].split(b"\r\n", 1)[1]

    # change the Accept-Encoding header value so the web server returns ascii
    start_index = request.find(b"Accept-Encoding:")
    if start_index != -1:
        request = request[:start_index] + b"Accept-Encoding: " + b"identity\r\n"\
                  + request[start_index:].split(b"\r\n", 1)[1]

    return request, host, path


def retrieve_webpage(host, path, request, sock):
    """
    Grabs web page from cache or retrieves from web server if not cached

    :param host: domain address of host
    :param path: path to requesting file
    :param request: request header from client
    :return: webpage from the web server or cache
    """
    # gets URL for saving cache files and replaces backslashes with space
    folder_name = "cache"
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    filename = host + b"$" + path.replace(b"/", b" ").strip()
    filename = filename.decode("utf-8")

    filepath = folder_name + "/" + filename

    # try to open cached file
    if os.path.exists(filepath):
        # compares the files age with the maximum allowed cache age
        m_seconds = os.path.getmtime(".\\" + filepath)
        curr_age = time.time() - m_seconds
        allowed_age = int(sys.argv[1])

        # removes expired caches
        if curr_age > allowed_age:
            # print(b"Updating old cache files for " + host + path.strip())
            os.remove(filepath)
            webpage = contact_webserver(host, request, sock)
            # saves webpage data in a file
            f = open(filepath, 'wb')
            f.write(webpage)

        else:
            f = open(filepath, 'rb')
            webpage = f.read()
            # print(b"got " + host + path.strip() + b" from cache")

    # get data if not cached
    else:
        # gets data from host server
        webpage = contact_webserver(host, request, sock)

        # saves webpage data in a file
        f = open(filepath, 'wb')
        f.write(webpage)
    return webpage


def handle_request(sock):
    """
    Receives request header from client then
    receives webpage and send it back to client

    :param sock: socket to requesting client
    :return: None
    """
    request = b""
    while True:
        data = sock.recv(1024)
        # print('{!r}'.format(data))
        if data:
            request += data
            if request[-4::] == b"\r\n\r\n":
                break
        else:
            # print('no data from', client_address)
            break

    if request == b'':
        return

    request, host, path = modify_header(request, sock)
    print(request)
    #print(socket_pairs)
    # get webpage and send it to client
    print(host)
    webpage = retrieve_webpage(host, path, request, sock)
    #print(webpage)
    sock.sendall(webpage)


socket_pairs = {}

if __name__ == "__main__":
    # creates socket
    inputs = []
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setblocking(False)
        server_address = ('localhost', 8888)
        server_sock.bind(server_address)
        server_sock.listen(5)

        inputs.append(server_sock)
        outputs = []

        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs,
                                                            inputs, 5)

            for s in readable:
                if s is server_sock:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                else:
                    if s.recv(1024, socket.MSG_PEEK) == b'':
                        if s in socket_pairs.keys():
                            socket_pairs[s]["sock"].close()
                            socket_pairs.pop(s, None)
                        inputs.remove(s)
                        s.close()
                    else:
                        handle_request(s)

            # socket_list = []
            # for s in socket_pairs.keys():
            #     if socket_pairs[s][].recv(1024, socket.MSG_PEEK) == b'':
            #         socket_list.append(s)
            #
            # for s in socket_list:
            #     print("closed")
            #     socket_pairs[s].close()
            #     socket_pairs.pop(s, None)

    except socket.error as e:
        print(e)

    for s in inputs:
        s.close()
    sys.exit(1)
