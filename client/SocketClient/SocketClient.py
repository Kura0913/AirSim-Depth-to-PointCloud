import socket 
import json
import gzip

BUFFER_SIZE = 67108864


class SocketClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.client_socket.connect((host, port))
    # send command to server
    def send_command(self, command, parameters):
        send_data = {'command': command, 'parameters': parameters}
        self.client_socket.send(gzip.compress(json.dumps(send_data).encode()))
    # wait response from server
    def wait_response(self):
        data = self.client_socket.recv(BUFFER_SIZE)
        raw_data = data.decode()
        print(f"The client received data => {raw_data}")
        
        return json.loads(raw_data)
