from DBController.DBConnection import DBConnection

class ColorInfoTable:
    def insert_colors(self, point_cloud_color_list):
        '''
        point_cloud_color_list = [
        [point_id, point_r, point_g, point_b]
        ]
        '''
        with DBConnection() as connection:
            for point_color_info in point_cloud_color_list:
                command = f"INSERT INTO color_info (point_id, point_r, point_g, point_b) VALUES  ('{point_color_info[0]}', '{point_color_info[1]}', '{point_color_info[2]}', '{point_color_info[3]}');"
                cursor = connection.cursor()
                cursor.execute(command)
        
            connection.commit()


    def select_all_color(self):
        '''
        Return : {
        "point_id" : [point_r, point_g, point_b]
        }
        '''
        point_color_dict = {}
        command = "SELECT * FROM color_info;"

        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        for row in record_from_db:
            point_color_dict[row['point_id']] = [row['point_r'], row['point_g'], row['point_b']]

        return point_color_dict
    
    def delete_all_colors(self):
        command = "DELETE FROM color_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()