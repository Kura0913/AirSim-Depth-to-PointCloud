from DBController.DBConnection import DBConnection

class PointCloudInfoTable:
    def insert_point_clouds(self, point_cloud_list):
        '''
        point_cloud_list = [
        [x_val, y_val, z_val]
        ]
        '''
        with DBConnection() as connection:  
            cursor = connection.cursor()
            
            # 使用唯一索引避免重複
            cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS unique_point 
            ON point_cloud_info (point_x, point_y, point_z)
            """)

            # 使用批量插入
            command = """
            INSERT OR IGNORE INTO point_cloud_info (point_x, point_y, point_z) 
            VALUES (?, ?, ?)
            """
            cursor.executemany(command, point_cloud_list)

            connection.commit()

    def select_a_point(self, point_cloud):
        '''
        Return : point_id,\n 
        if the point is not exist, return -1.
        '''
        command = f"SELECT * FROM point_cloud_info WHERE point_x ='{point_cloud[0]}' AND point_y ='{point_cloud[1]}' AND point_z ='{point_cloud[2]}';"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        try:
            return [row['point_id'] for row in record_from_db][0]
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
            cursor = connection.cursor()
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