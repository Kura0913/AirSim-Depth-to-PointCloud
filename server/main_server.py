from SocketServer.SocketServer import SocketServer
from SocketServer.JobDispatcher import JobDisPatcher
from DBController.DBConnection import DBConnection
from DBController.DBInitializer import DBInitializer
from DBController.MongoDBConnection import MongoDBConnection
import os
import socket

def main():
    # setting socket connection ip and port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    port = 40005
    # initial sqlite database for save drone infiormation
    if os.path.exists("vehicle_info.db"):
        os.remove("vehicle_info.db")
    DBConnection.db_file_path = "vehicle_info.db"
    DBInitializer().execute()
    job_dispatcher = JobDisPatcher()
    # initial mongoDB connection for save point cloud information    
    atlas_uri = "mongodb://localhost:27017/"
    mongodb_name = "aiotlab"
    collection_name = 'point_cloud_info'

    MongoDBConnection.initialize(atlas_uri, mongodb_name)
    mongodb = MongoDBConnection()    
    if not mongodb.ping():
        exit()
    # connect to mongodb's collection
    point_cloud_collection = mongodb.get_collection(collection_name)
    mongodb.create_indexes(collection_name)
    # make sure the collection is empty
    point_cloud_collection.delete_many({})

            

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