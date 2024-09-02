from DBController.SqliteDBConnection import DBConnection

class DroneInfoTable:
    def insert_a_drone(self, drone_name):
        command = f"INSERT INTO drone_info (name) VALUES ('{drone_name}');"
        
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()


    def select_a_drone(self, drone_name):
        '''
        Return: [drone_id]
        '''
        command = f"SELECT * FROM drone_info WHERE name='{drone_name}';"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        drone_info = []
        if len(record_from_db) > 0:
            for row in record_from_db:
                drone_info.append(row['drone_id'])
        return drone_info
    
    def delete_all_drone(self):
        command = "DELETE FROM drone_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()