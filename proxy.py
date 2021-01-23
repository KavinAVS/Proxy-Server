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
        while True:
            data = connection.recv(16)
            print('received {!r}'.format(data))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no data from', client_address)
                break

    finally:
        #close connecton
        connection.close()