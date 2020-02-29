
import errno
import queue
import select
import socket
import sys

class ServerSocket:
    def __init__(self, mode, port, read_callback, max_connections, recv_bytes):
        # Handle the socket's mode.
        # The socket's mode determines the IP address it binds to.
        # mode can be one of two special values:
        # localhost -> (127.0.0.1)
        # public ->    (0.0.0.0)
        # otherwise, mode is interpreted as an IP address.
        if mode == "localhost":
            self.ip = mode
        elif mode == "public":
            self.ip = socket.gethostname()
        else:
            self.ip = mode
        # Handle the socket's port.
        # This should be a high (four-digit) for development.
        self.ip = ''
        self.port = 12345
        queues = dict()
        # Create a similar dictionary that stores IP addresses.
        # This dictionary maps sockets to IP addresses
        IPs = dict()
        # Now, the main loop.
        while readers:
            # Block until a socket is ready for processing.
            read, write, err = select.select(readers, writers, readers)
            # Deal with sockets that need to be read from.
            for sock in read:
                if sock is self._socket:
                    # We have a viable connection!
                    client_socket, client_ip = self._socket.accept()
                    # Make it a non-blocking connection.
                    client_socket.setblocking(0)
                    # Add it to our readers.
                    readers.append(client_socket)
                    # Make a queue for it.
                    queues[client_socket] = queue.Queue()
                    # Store its IP address.
                    IPs[client_socket] = client_ip
                else:
                    # Someone sent us something! Let's receive it.
                    data = sock.recv(self.recv_bytes)
                    try:
                        data = sock.recv(self.recv_bytes)
                    except socket.error as e:
                        if e.errno is errno.ECONNRESET:
                            # Consider 'Connection reset by peer'
                            # the same as reading zero bytes
                            data = None
                        else:
                            raise e
                    if data:
                        # Call the callback
                        self.callback(IPs[sock], queues[sock], data)


