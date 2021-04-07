# text_receive_client.py

import socket
import select
import threading
import time

HOST = 'localhost'
PORT = 65439

ACK_TEXT = 'RECEIVED_SUCC'


class Client:

    def startClient(self):
        # instantiate a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('socket instantiated')

        # connect the socket
        connectionSuccessful = False

        while True:
            if not connectionSuccessful:
                try:
                    sock.connect((HOST,
                                  PORT))  # Note: if execution gets here before the server starts up, this line will cause an error, hence the try-except
                    print('socket connected to server')
                    connectionSuccessful = True
                except:
                    pass
            else:
                try:
                    socks = [sock]
                    readySocks, _, _ = select.select(socks, [], [], 5)
                    for sock in readySocks:
                        message = self.receiveTextViaSocket(sock)
                        print('received: ' + str(message))
                        ## TODO: Update Postion and game status variables form CAR Object here!
                # if server connection gets lost, instantiate new socket and wait for server connection!
                except ConnectionResetError:
                    print("Connection to server lost - wait for new connection!")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("Instantiated new client socket!")
                    connectionSuccessful = False
                    pass

    # end function

    def receiveTextViaSocket(self, sock):
        # get the text via the scoket
        encodedMessage = sock.recv(1024)

        # if we didn't get anything, log an error and bail
        if not encodedMessage:
            print('error: encodedMessage was received as None')
            return None
        # end if

        # decode the received text message
        message = encodedMessage.decode('utf-8')

        # now time to send the acknowledgement
        # encode the acknowledgement text
        encodedAckText = bytes(ACK_TEXT, 'utf-8')
        # send the encoded acknowledgement text
        sock.sendall(encodedAckText)

        return message

    # end function


if __name__ == '__main__':
    ## Include this code into main of Player class
    client = Client()
    threading.Thread(target=client.startClient()).start()
