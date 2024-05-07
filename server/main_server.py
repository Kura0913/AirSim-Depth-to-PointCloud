from SocketServer.SocketServer import SocketServer
from SocketServer.JobDispatcher import JobDisPatcher
from DBController.DBConnection import DBConnection
from DBController.DBInitializer import DBInitializer
import os
import socket

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = 40005
    if os.path.exists("point_cloud.db"):
        os.remove("point_cloud.db")
    DBConnection.db_file_path = "point_cloud.db"
    DBInitializer().execute()
    job_dispatcher = JobDisPatcher()

    server = SocketServer(job_dispatcher, ip, port)
    server.daemon = True
    server.serve()

    print("Server start...")
    print(f"Server ip: {ip} port: {port}")
    # because we set daemon is true, so the main thread has to keep alive
    while True:
        command = input()
        if command == "finish":
            break
    
    server.server_socket.close()
    print("leaving ....... ")

if __name__ == "__main__":
    main()