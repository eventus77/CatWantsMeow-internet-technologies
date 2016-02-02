import json
import logging
import socket


logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s')


class Chat(object):

    def __init__(self):
        pass

    def connect_client(self, data, address):
        pass

    def disconnect_client(self, data, address):
        pass

    def post_message(self, data, address):
        pass


class Server(object):

    CLIENT_CONNECTED = 0
    CLIENT_DISCONNECTED = 1
    MESSAGE_POSTED = 2
    MESSAGE_CODES = [CLIENT_CONNECTED, CLIENT_DISCONNECTED, MESSAGE_POSTED]

    def __init__(self, host, port, max_message_length=1024, thread_blocking=True):
        self.host = host
        self.port = port
        self.max_message_length = max_message_length
        self.thread_blocking = thread_blocking

        self.chat = Chat()
        self.message_handlers = {
            self.CLIENT_CONNECTED: self.chat.connect_client,
            self.CLIENT_DISCONNECTED: self.chat.disconnect_client,
            self.MESSAGE_POSTED: self.chat.post_message,
        }

        try:
            self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.listener.bind((host, port))
        except socket.error as e:
            logging.error('Server initialization has failed: {error[1]}(code: {error[0]})'.format(error=e))
        except Exception as e:
            logging.error('Server initialization has failed: {error}'.format(error=e))

    def create_error_data(self, result, message):
        error_data = {"result": result, "message": message}
        return json.dumps(error_data)

    def receive_message(self):
        try:
            message, sender = self.listener.recvfrom(self.max_message_length)
            return message, sender
        except socket.error as e:
            logging.error('Error while receiving a message: {error[1]}(code: {error[0]})'.format(error=e))
        except Exception as e:
            logging.error('Error while receiving a message: {error)'.format(error=e))

    def parse_message(self, message, address):
        try:
            message_obj = json.loads(message)
        except ValueError:
            logging.warning('Wrong message format: {message}'.format(message))
            error_data = {"result": "failed", "message": "Wrong message format"}
            return json.dumps(error_data)

        message_code = message_obj.get('code', None)
        if message_code is None:
            logging.warning('Message without code has been received')
            return self.create_error_data("failed", "Message without code")
        elif message_code not in self.MESSAGE_CODES:
            logging.warning("Message with unknown code has been received: {code}".format(message_obj['code']))
            return self.create_error_data("failed", "Message have unknown code")
        else:
            try:
                message_handler = self.message_handlers[message_code]
                reply_data = message_handler(message["data"], address)
                return reply_data
            except KeyError as e:
                logging.warning("Message without data has been received")
                return self.create_error_data("failed", "Message without data")

    def send_reply(self, message, address):
        try:
            self.listener.sendto(message, address)
        except socket.error as e:
            logging.error('Error while receiving a message: {error[1]}(code: {code[0]})'.format(e))
        except Exception as e:
            logging.error('Error while receiving a message: {error})'.format(e))

    def start_server(self):
        try:
            while True:
                message, sender = self.receive_message()
                reply = self.parse_message(message)
                self.send_reply(reply, sender)
        except KeyboardInterrupt:
            self.close()
            return

    def close(self):
        self.listener.close()

Server()