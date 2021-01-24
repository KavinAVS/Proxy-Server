import sys, os, time, socket, select

def get_header_val(name, header):
    index = header.find(name)
    index += len(name)+1
    num = header[index:].split(b"\r\n", 1)
    return num[0].strip()

def receive_webinfo(webaddress, request):
    webpage = b""
    try:
        print("here")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (webaddress, 80)
        print("here")
        sock.connect(server_address)
        sock.sendall(request)

        data = sock.recv(1024)
        content_len = int(get_header_val(b"Content-Length", data))

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
        #sys.exit(1)

    else:
        sock.close()

    return webpage

if __name__ == "__main__":
    # creates socket
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8888)
        server_sock.bind(server_address)
        server_sock.listen(1)
    except Exception:
        sys.exit(1)

    while True:
        # wait for connection
        connection, client_address = server_sock.accept()

        try:
            # Receive the data in small chunks and retransmit it
            request = b""
            while True:
                data = connection.recv(1024)
                #print('{!r}'.format(data))
                if data:
                    request += data
                    if request[-4::] == b"\r\n\r\n":
                        break
                else:
                    #print('no data from', client_address)
                    break

            #print("here")
            #start_index = request.find(b"Host:")
            #request = request[:start_index] + request[start_index:].split(b"\r\n", 1)[1]
            print(request)

            web_address = request.split(b" ", 2)[1].strip(b"/")
            print(web_address)
            webpage = receive_webinfo(web_address, request)
            print(webpage)
            connection.sendall(webpage)


        finally:
            # close connecton
            connection.close()
