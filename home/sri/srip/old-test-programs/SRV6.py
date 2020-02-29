
import logging
import socketserver


class EchoHandler(socketserver.BaseRequestHandler):
    BUFFER_SIZE = 1024
    # size limit in bytes for the client message to be received
    MAX_MSG_SIZE = 1024 * 5

    def finish(self):
        self.request.close()

    def handle(self):
        msg = self.get_client_msg()
        logging.info('Client: %s sent %d bytes as this: %s text-msg ', self.client_address, len(msg), msg)

        sent_bytes = self.send_client_msg(msg)
        logging.info('Server sent %d bytes to client: %r', sent_bytes, self.client_address)

    def get_client_msg(self):
        data = b''
        while True:
            buf = self.request.recv(self.BUFFER_SIZE)
            data += buf
            if not buf or len(data) >= self.MAX_MSG_SIZE:
                return data

    def send_client_msg(self, msg):
        total_sent = 0
        message = memoryview(msg)

        while True:
            try:
                sent_bytes = self.request.send(message[total_sent:])
                total_sent += sent_bytes

                if sent_bytes == 0:
                    return total_sent
            except ConnectionResetError:
                # in case client disconnected before we send the echo
                logging.info('Client %r disconnected before sending echo.', self.client_address)
                return total_sent


class EchoServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

    def process_request(self, request, client_address):
        logging.info('Connection from client %r', client_address)
        super().process_request(request, client_address)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with EchoServer(('10.249.1.3', 12345), EchoHandler) as server:
        print("server on")
        server.serve_forever()
