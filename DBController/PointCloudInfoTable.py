from DBController.DBConnection import DBConnection

class PointCloudInfoTable:
    def insert_point_clouds(self, point_cloud_list):
        for point_cloud in point_cloud_list:
            command = f"INSERT INTO drone_info (point_x, point_y, point_z) VALUES  ('{point_cloud[0]}', '{point_cloud[1]}', '{point_cloud[2]}');"
            with DBConnection() as connection:
                cursor = connection.cursor()
                cursor.execute(command)
        
        connection.commit()