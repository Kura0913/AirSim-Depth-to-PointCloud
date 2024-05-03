from DBController.DBConnection import DBConnection

class PointCloudInfoTable:
    def insert_point_clouds(self, point_cloud_list):
        with DBConnection() as connection:
            for point_cloud in point_cloud_list:
                if self.select_a_point(point_cloud[0], point_cloud[1], point_cloud[2]) >= 0:
                    continue
                command = f"INSERT INTO drone_info (point_x, point_y, point_z) VALUES  ('{point_cloud[0]}', '{point_cloud[1]}', '{point_cloud[2]}');"
                cursor = connection.cursor()
                cursor.execute(command)
        
        connection.commit()

    def select_a_point(self, point_cloud):
        command = f"SELECT * FROM student_info WHERE x ='{point_cloud[0]}' AND y ='{point_cloud[1]} AND z ='{point_cloud[2]};"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        try:
            return [row['point_id'] for row in record_from_db][0]
        except Exception as e:
            return -1
        

    def select_all_points(self):
        point_dict = {}
        command = "SELECT * FROM point_cloud_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()
        for row in record_from_db:
            point_dict[row['point_id']] = [row['x'], row['y'], row['z']]

        return point_dict