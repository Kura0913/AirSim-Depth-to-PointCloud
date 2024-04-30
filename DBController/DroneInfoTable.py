from DBController.DBConnection import DBConnection

class DroneInfoTable:
    def insert_a_drone(self, drone_name):
        command = f"INSERT INTO drone_info (name) VALUES  ('{drone_name}');"
        
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()