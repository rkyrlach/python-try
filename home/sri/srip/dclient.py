
import socket
import sys

#def echoipad()


messages = [ 'This is the message. ',
             'It will be sent ',
             'in parts.',
             ]
server_address = ('10.249.1.3', 12345)

# Create a TCP/IP socket
socks = [ socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          socket.socket(socket.AF_INET, socket.SOCK_STREAM),
          ]

# Connect the socket to the port where the server is listening
print >>sys.stderr, 'connecting to %s port %s' % server_address
for s in socks:
    s.connect(server_address)

for message in messages:

    # Send messages on both sockets
    for s in socks:
        print >>sys.stderr, '%s: sending "%s"' % (s.getsockname(), message)
        s.send(message)

    # Read responses on both sockets
    for s in socks:
        data = s.recv(1024)
        print >>sys.stderr, '%s: received "%s"' % (s.getsockname(), data)
        if not data:
            print >>sys.stderr, 'closing socket', s.getsockname()
            s.close()



#import socket

#def echoipad()

#def Main():
#        global message
        # local host IP '127.0.0.1'
#        host = '10.249.1.3'
        # Define the port on which you want to connect
#        port = 12345
#        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        # connect to server on local computer
#        s.connect((host,port))
#        while True:
                # message sent to server
#                print("enter a command: (eg t,600 or t,-600)" )
#                command = input()
#                s.send(command.encode('ascii'))
                # messaga received from serve
                # print the received message
#                print('Received from the server :',str(data.decode('ascii')))
                # ask the client whether he wants to continue
#                ans = input('\nDo you want to continue(y/n) :')
#                if ans == 'y':
#                        continue
#                else:
#                        break
        # close the connection
#        s.close()

#if __name__ == '__main__':
#        Main()

