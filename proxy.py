import sys, os, time, socket, select

# creates socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# links socket to port
server_address = ('localhost', 8888)
sock.bind(server_address)

# listen for connections
sock.listen(1)

while True:
    # wait for connection
    connection, client_address = sock.accept()

    try:
        # Receive the data in small chunks and retransmit it
        request = b''
        while True:
            data = connection.recv(1024)
            print('{!r}'.format(data))
            if data:
                request += data
            else:
                # print('no data from', client_address)
                break

    finally:
        #close connecton
        connection.close()
