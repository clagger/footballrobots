# text_receive_client.py
import json
import socket
import select
import struct
import threading
import time
import jsonpickle

default_host = 'localhost'
PORT = 65439

ACK_TEXT = 'RECEIVED_SUCC'


def saveDataToPlayer(message, player):
    """  reads JSON messge, deserialize it and update game_data of player object

    """
    currentGameData = jsonpickle.loads(message)
    player.game_data = currentGameData

    ## old parsing of json data
    """for r_p_coordinate in jsonData['playerCoordinates']:
        for coordinate in player.gameCoordinates.playerCoordinates:
            if coordinate.player_id == r_p_coordinate['player_id']:
                coordinate.pos_x = r_p_coordinate['pos_x']
                coordinate.pos_y = r_p_coordinate['pos_y']
                coordinate.rot = r_p_coordinate['rot']
    player.gameCoordinates.ballCoordinates.pos_x = jsonData['ballCoordinates']['pos_x']
    player.gameCoordinates.ballCoordinates.pos_y = jsonData['ballCoordinates']['pos_y']"""


class Client:

    def startClient(self, player, server_ip):
        """  starts client socket which accepts server messages

        """
        # instantiate a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('socket instantiated')

        if server_ip:
            HOST = server_ip
        else:
            HOST = default_host

        print("Using Server IP: " + HOST)

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
                        saveDataToPlayer(message, player)


                # if server connection gets lost, instantiate new socket and wait for server connection!
                except ConnectionResetError:
                    print("Connection to server lost - wait for new connection!")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("Instantiated new client socket!")
                    connectionSuccessful = False
                    pass

    # end function
    def socket_read_n(self, sock, n):
        """ Read exactly n bytes from the socket.
            Raise RuntimeError if the connection closed before
            n bytes were read.
        """
        buf = b''
        while n > 0:
            data = sock.recv(n)
            if data == '':
                raise RuntimeError('unexpected connection close')
            buf += data
            n -= len(data)
        return buf

    def receiveTextViaSocket(self, sock):
        """  receives message from server
             reads first 4 positions for length
             read length from socket (=game_data serialized in JSON format)

        """
        # get the text via the socket

        len_buf = self.socket_read_n(sock, 4)
        msg_len = struct.unpack('>L', len_buf)[0]
        encodedMessage = self.socket_read_n(sock, msg_len)

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
