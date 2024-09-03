from SocketServer.SocketServer import SocketServer
from SocketServer.JobDispatcher import JobDisPatcher
from DBController.DBInitializer import DBInitializer
import socket

sqlite_db_path = "../vehicle_info.db"

def main():
    # setting socket connection ip and port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = 40005
    # connect to mysql database
    mysql_db = DBInitializer()
    mysql_db.execute()

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