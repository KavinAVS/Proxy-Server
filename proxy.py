import sys, os, time, socket, select

# creates socket
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# links socket to port
server_address = ('localhost', 8888)
serv_sock.bind(server_address)

# listen for connections
serv_sock.listen(1)

while True:
    # wait for connection
    connection, client_address = sevr_sock.accept()

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
        
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


            

    finally:
        #close connecton
        connection.close()
