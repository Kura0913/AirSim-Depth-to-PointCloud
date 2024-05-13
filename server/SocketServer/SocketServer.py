from SocketServer import JobDispatcher
from threading import Thread
import socket
import json

BUFFER_SIZE = 33554432

class SocketServer(Thread):
    def __init__(self, job_dispatcher, host, port=40005):
        super().__init__()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # The following setting is to avoid the server crash. So, the binded address can be reused
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        self.job_dispatcher = job_dispatcher

    def serve(self):
        self.start()

    def run(self):
        while True:
            connection, address = self.server_socket.accept()
            print(f"{address} connected")
            self.new_connection(connection=connection,
                                address=address)


    def new_connection(self, connection, address):
        Thread(target=self.receive_message_from_client,
               kwargs={
                   "connection": connection,
                   "address": address}, daemon=True).start()

    def receive_message_from_client(self, connection, address):
        # get students list        
        keep_going = True
        while keep_going:
            try:
                message = connection.recv(1024).strip().decode()
                message = json.loads(message)
            except Exception as e:
                print(f"Exeption happened {e}, {address}")
                keep_going = False
            else:
                if not message['parameters']:
                    keep_going = False
                else:                    
                    print(f'The server received message=>{message}')
                    result_message = self.job_dispatcher.job_execute(message["command"], message["parameters"])
                    connection.send(json.dumps(result_message).encode())
                    print(f"The server sent data =>{result_message}")
        
        connection.close()
        print(f"{address} close connection")