import logging
import socket, sys
import struct
import threading

TCP_IP_DEFAULT = 'localhost'
TCP_PORT = 65439
BUFFER_SIZE = 1024  # Max size in byte of transmitted ACK message
clientCount = 0


def get_host_ip():
    """ get host IP, only IPs in own Wifi Router are accepted

    """
    for x in [i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None)]:
        if "192.168.0." in x:
            return x


class Server:

    def __init__(self):
        self.CLIENTS = []

    def startServer(self):
        """  starts server socket on port 65439
             handles incoming client registering and starts own thread for client messaging for each client
        """
        try:
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            TCP_IP = get_host_ip()
            if not TCP_IP:
                TCP_IP = TCP_IP_DEFAULT
            print("SERVER: Start listening on: IP {0} Port {1}".format(TCP_IP, TCP_PORT))
            serverSocket.bind((TCP_IP, TCP_PORT))
            serverSocket.listen(10)
            while True:
                client_socket, addr = serverSocket.accept()
                logging.info('Connected with ' + addr[0] + ':' + str(addr[1]))
                # register client
                self.CLIENTS.append(client_socket)
                # start own thread for each client
                threading.Thread(target=self.clientHandler, args=(client_socket,)).start()
            serverSocket.close()
        except socket.error as msg:
            print('SERVER: Could Not Start Server Thread. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

    # client handler - one of these loops is running for each client to receive ACK Messages
    #                - own thread for each client
    def clientHandler(self, client_socket):
        """  client handler which receives ACK messages from server for each message

        """
        while True:
            try:
                # receive ACK data from client
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break
            except ConnectionResetError:
                print("Lost connection to client: " + str(client_socket))
                break
        # the connection is closed:
        # unregister client from list, close socket and kill client thread
        self.CLIENTS.remove(client_socket)
        client_socket.close()
        sys.exit()
        # client_socket.close() #do we close the socket when the program ends? or for ea client thead?

    def broadcast(self, message):
        """  broadcasts message to each connected client

        """
        for sock in self.CLIENTS:
            try:
                packed_length = struct.pack('>L', len(message))
                data = packed_length + (bytes(message, 'utf-8'))
                sock.sendall(data)
            except socket.error:
                sock.close()  # closing the socket connection
                self.CLIENTS.remove(sock)  # removing the socket from the active connections list
