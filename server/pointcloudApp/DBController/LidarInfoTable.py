from DBController.DBConnection import DBConnection

class LidarInfoTable:
    '''
    drone_id INTEGER,\n
    lidar_face INTEGER,\n
    translation_x FLOAT,\n
    translation_y FLOAT,\n
    translation_z FLOAT,\n
    quaternion_w FLOAT,\n
    quaternion_x FLOAT,\n
    quaternion_y FLOAT,\n
    quaternion_z FLOAT\n
    '''
    def insert_lidars(self, parameters):
        '''
        parameters:{
            lidar_face:{
                drone_id : integer,\n 
                translation: [x_val, y_val, z_val],\n 
                quaternion: [w_val, x_val, y_val, z_val]
            }
        }
        '''        
        with DBConnection() as connection:
            cursor = connection.cursor()
            for lidar_face, lidar_info in parameters.items():
                command = """
                INSERT INTO lidar_info 
                (drone_id, lidar_face, translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(command, (
                    lidar_info['drone_id'],
                    lidar_face,
                    lidar_info['translation'][0],
                    lidar_info['translation'][1],
                    lidar_info['translation'][2],
                    lidar_info['quaternion'][0],
                    lidar_info['quaternion'][1],
                    lidar_info['quaternion'][2],
                    lidar_info['quaternion'][3]
                ))
            connection.commit()

    def select_a_lidar(self, drone_id, lidar_face):
        '''
        Return : [translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z](list)
        '''
        command = """
        SELECT translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z
        FROM lidar_info
        WHERE drone_id = %s AND lidar_face = %s;
        """
        with DBConnection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(command, (drone_id, lidar_face))
            record_from_db = cursor.fetchall()

        if record_from_db:
            row = record_from_db[0]
            result = [
                row['translation_x'],
                row['translation_y'],
                row['translation_z'],
                row['quaternion_w'],
                row['quaternion_x'],
                row['quaternion_y'],
                row['quaternion_z']
            ]
            return result
        else:
            return []

    def delete_all_lidar(self):
        command = "DELETE FROM lidar_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
