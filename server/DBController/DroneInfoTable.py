from DBController.DBConnection import DBConnection

class DroneInfoTable:
    def insert_a_drone(self, drone_name, fov, width, height):
        command = f"INSERT INTO drone_info (name, fov, image_width, image_hieght) VALUES  ('{drone_name, fov, width, height}');"
        
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()


    def select_a_drone(self, drone_name):
        '''
        Return: [drone_id, fov, width, height]
        '''
        command = f"SELECT * FROM drone_info WHERE name ='{drone_name};'"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        drone_info = []
        for row in record_from_db:
            drone_info = [row['drone_id'], row['fov'], row['width'], row['height']]

        return drone_info
    
    def delete_all_drone(self):
        command = "DELETE FROM drone_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()