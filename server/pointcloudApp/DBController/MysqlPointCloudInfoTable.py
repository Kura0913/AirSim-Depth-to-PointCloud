import mysql.connector
from DBController.MysqlDBConnection import DBConnection

class MysqlPointCloudInfoTable:
    def insert_point_clouds(self, point_cloud_list):
        '''
        point_cloud_list = [
        [x_val, y_val, z_val]
        ]
        '''
        with DBConnection() as connection:  
            cursor = connection.cursor()
            
            cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_point 
            ON point_cloud_info (point_x, point_y, point_z)
            """)

            command = """
            INSERT IGNORE INTO point_cloud_info (point_x, point_y, point_z) 
            VALUES (%s, %s, %s)
            """
            cursor.executemany(command, point_cloud_list)

            connection.commit()

    def insert_point_clouds_with_color(self, point_cloud_list, color_list):
        '''
        point_cloud_list = [
        [x_val, y_val, z_val]
        ]
        color_list = [
        [r, g, b]
        ]
        '''

        point_cloud_list_with_color = [point + color for point, color in zip(point_cloud_list, color_list)]
        with DBConnection() as connection:  
            cursor = connection.cursor()
            # check unique index wheather exist
            cursor.execute("SHOW INDEX FROM point_cloud_info WHERE Key_name = 'unique_point'")
            result = cursor.fetchone()

            # Clear any unread results
            cursor.fetchall()
            # if unique index not exist, create it
            if not result:
                cursor.execute("""
                CREATE UNIQUE INDEX unique_point 
                ON point_cloud_info (point_x, point_y, point_z)
                """)
                print("Unique index created.")

            command = """
            INSERT IGNORE INTO point_cloud_info (point_x, point_y, point_z, color_r, color_g, color_b) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(command, point_cloud_list_with_color)

            connection.commit()

    def select_a_point(self, point_cloud):
        '''
        Return : point_id,
        if the point is not exist, return -1.
        '''
        command = f"SELECT point_id FROM point_cloud_info WHERE point_x = %s AND point_y = %s AND point_z = %s"
        with DBConnection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(command, (point_cloud[0], point_cloud[1], point_cloud[2]))
            record_from_db = cursor.fetchall()
        try:
            return record_from_db[0]['point_id'] if record_from_db else -1
        except Exception as e:
            return -1

    def select_all_points(self):
        '''
        Return : {
        "point_id" : [x_val, y_val, z_val]
        }
        '''
        point_dict = {}
        command = "SELECT * FROM point_cloud_info;"
        with DBConnection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        for row in record_from_db:
            point_dict[row['point_id']] = [row['point_x'], row['point_y'], row['point_z']]

        return point_dict
    
    def delete_all_points(self):
        command = "DELETE FROM point_cloud_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()