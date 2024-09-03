from DBController.DBConnection import DBConnection

class CameraInfoTable:
    def insert_cameras(self, parameters):
        '''
        parameters:{
            camera_face:{
                drone_id : integer,\n 
                translation: [x_val, y_val, z_val],\n 
                quaternion: [w_val, x_val, y_val, z_val],
                fov: float,
                width: INTEGER,
                height: INTEGER
            }
        }
        '''        
        with DBConnection() as connection:
            cursor = connection.cursor()
            for camera_face, camera_info in parameters.items():
                command = """
                INSERT INTO camera_info 
                (drone_id, camera_face, translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z, fov, width, height) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(command, (
                    camera_info['drone_id'], camera_face, 
                    camera_info['translation'][0], camera_info['translation'][1], camera_info['translation'][2],
                    camera_info['quaternion'][0], camera_info['quaternion'][1], camera_info['quaternion'][2], camera_info['quaternion'][3],
                    camera_info['fov'], camera_info['width'], camera_info['height']
                ))
            
            connection.commit()

    def select_a_camera(self, drone_id, camera_face):
        '''
        Return : 
        {
            "translate": (list),
            "quaternion": (list),
            "fov": float,
            "width": int,
            "height": int
        }
        '''
        command = "SELECT * FROM camera_info WHERE drone_id=%s AND camera_face=%s;"
        with DBConnection() as connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(command, (drone_id, camera_face))
            record_from_db = cursor.fetchall()

        if record_from_db:
            row = record_from_db[0]
            result = {
                "translate": [row['translation_x'], row['translation_y'], row['translation_z']],
                "quaternion": [row['quaternion_w'], row['quaternion_x'], row['quaternion_y'], row['quaternion_z']],
                "fov": row['fov'],
                "width": row['width'],
                "height": row['height']
            }
            return result
        else:
            return dict()

    def delete_all_camera(self):
        command = "DELETE FROM camera_info;"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()
