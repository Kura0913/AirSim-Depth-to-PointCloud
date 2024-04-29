from SocketServer.SocketServer import SocketServer
from SocketServer.JobDispatcher import JobDisPatcher
from DBController.DBConnection import DBConnection
from DBController.DBInitializer import DBInitializer

def main():
    DBConnection.db_file_path = "point_cloud.db"
    DBInitializer().execute()
    job_dispatcher = JobDisPatcher()

    server = SocketServer(job_dispatcher, "127.0.0.1", 40005)
    server.daemon = True
    server.serve()

    # because we set daemon is true, so the main thread has to keep alive
    while True:
        command = input()
        if command == "finish":
            break
    
    server.server_socket.close()
    print("leaving ....... ")   


if __name__ == "__main__":
    main()