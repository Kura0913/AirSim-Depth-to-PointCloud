import mysql.connector

class DBConnection:
    def __enter__(self):
        self.connection = mysql.connector.connect(
            host='localhost',           # MySQL ip
            user='root',                # MySQL user name
            password='aiotlab',         # MySQL password
            database='point_cloud_db'   # MySQL database name
        )
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()