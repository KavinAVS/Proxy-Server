import sys, os, time, socket, select


def get_header_val(name, header):
    index = header.find(name)
    if index == -1:
        return -1
    index += len(name)+1
    num = header[index:].split(b"\r\n", 1)
    return num[0].strip()


def receive_webinfo(webaddress, request):
    webpage = b""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        address = (webaddress, 80)
        sock.connect(address)
        sock.sendall(request)

        data = sock.recv(1024)
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

    except Exception:
        print("Unable to connect to web server")
        sock.close()

    else:
        sock.close()

    return webpage


def handle_request(sock):
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

    start_index = request.find(b"Host:")
    if start_index != -1:
        request = request[:start_index] + request[start_index:].split(b"\r\n", 1)[1]

    # get web address and add http:// to the header's address
    temp = request.split(b" ", 2)
    web_address = temp[1].split(b"/")[1]  #get address ([0] is empty since it starts with /)
    request = temp[0] + b" http://" + temp[1].strip(b"/") + b" " + temp[2]

    webpage = receive_webinfo(web_address, request)
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
                                                            inputs)

            for s in readable:
                if s is server_sock:
                    connection, client_address = s.accept()
                    connection.setblocking(0)
                    inputs.append(connection)
                else:
                    handle_request(s)

    except socket.error as e:
        print(e)

    for s in inputs:
        s.close()
    sys.exit(1)
