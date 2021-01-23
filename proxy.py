import sys, os, time, socket, select

def receive_webinfo(webaddress, request):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (webaddress, 80)
    sock.connect(server_address)
    print("here1")
    try:
        sock.sendall(request)
        data = sock.recv(1024)

        #finds content length
        start = s.find('Content-Length:')
        start += 16
        end = start
        while (s[end]).isdigit():
            end += 1
        content_length = s[start:end]

        #get rest of the data
        # webpage = b''
        # while True:
        #     data = sock.recv(1024)
        #     print('{!r}'.format(data))
        #     if data:
        #         webpage += data
        #     else:
        #         print('no data from', client_address)
        #         break
        print("here2")
    finally:
        sock.close()

    print("here")

    return webpage

if __name__ == "__main__":
    # creates socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # links socket to port
    server_address = ('localhost', 8888)
    server_sock.bind(server_address)

    # listen for connections
    server_sock.listen(1)

    while True:
        # wait for connection
        connection, client_address = server_sock.accept()

        try:
            # Receive the data in small chunks and retransmit it
            request = b''
            while True:
                data = connection.recv(1024)
                #print('{!r}'.format(data))
                if data:
                    request += data
                else:
                    # print('no data from', client_address)
                    break

            web_address = request.split(b" ", 2)[1].strip(b"/")
            webpage = receive_webinfo(web_address, request)
            print(webpage)
            #connection.sendall(webpage)


        finally:
            # close connecton
            connection.close()
