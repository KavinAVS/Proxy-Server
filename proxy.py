import sys, os, time, socket, select


def add_cache_box(webpage, state):
    """
    Adds a notification box in html recieved from the webpage indicating
    if the webpage is fresh or cached.
    webpage: the HTML header/code to modify
    state: either fresh or cached
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


def contact_webserver(webaddress, request):
    """
    Creates a client to request data from given web address using the
    request header
    :param webaddress: The address of the web server
    :param request: The request header to send to the web server
    :return: the webpage/file sent by the web server
    """
    webpage = b""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        address = (webaddress, 80)
        sock.connect(address)
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
                sock.close()
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

    else:
        sock.close()

    return webpage


def retrieve_webpage(host, path, request):
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
            print("Updating cache files")
            os.remove(filepath)

            webpage = contact_webserver(host, request)
            print("FUNCTION OUTPUT")
            print (get_header_val(b"Accept:", webpage))
            if (get_header_val(b"Accept:", webpage) == b"text/html"):
                print("WE GOT AN HTML FILE IN DA HOUSEEEEEEE\n")
            
            #index = webpage.find("<body>")



            # saves webpage data in a file
            f = open(filepath, 'wb')
            f.write(webpage)
            f.close()

        else:
            f = open(filepath, 'rb')
            webpage = f.read()
            print("got from cache")
            f.close()

    # get data if not cached
    else:
        # gets data from host server
        webpage = contact_webserver(host, request)
        print("FUNCTION OUTPUT")
        print (get_header_val(b"Accept", webpage))

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
        print('{!r}'.format(data))
        if data:
            request += data
            if request[-4::] == b"\r\n\r\n":
                break
        else:
            # print('no data from', client_address)
            break

    if request == b'':
        return

    # get web address
    temp = request.split(b" ", 2)
    address_parts = temp[1].split(b"/", 2)
    host = address_parts[1]  # since address starts with / [1] is the domain

    # change GET path
    path = b""
    if len(address_parts) < 3:
        path = b" / "
        # if the address is "/www.example.com" then this only has 2 parts
    else:
        path = b" /" + address_parts[2] + b" "
    request = temp[0] + path + temp[2]

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

    # get webpage and send it to client
    webpage = retrieve_webpage(host, path, request)
    print("WEBPAGE:")
    print(webpage)
    sock.sendall(webpage)


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
                                                            inputs, 10)

            for s in readable:
                if s is server_sock:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                else:
                    if s.recv(1024, socket.MSG_PEEK) == b'':
                        s.close()
                        inputs.remove(s)
                    else:
                        handle_request(s)

    except socket.error as e:
        print(e)

    for s in inputs:
        s.close()
    sys.exit(1)
