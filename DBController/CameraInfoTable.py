from DBController.DBConnection import DBConnection

class CameraInfoTable:
    def insert_a_camera(self, parameters):
        '''
        parameters:{
            camera_face:{
                drone_id, translation(List), quaternion(List)
            }
        }
        '''        
        with DBConnection() as connection:
            for camera_face, camera_info in parameters.items():
                command = f"INSERT INTO camera_info (drone_id, camera_face, translation_x,, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z) VALUES  ('{camera_info['drone_id']}', '{camera_face}', '{camera_info['translation'][0]}', '{camera_info['translation'][1]}', '{camera_info['translation'][2]}', '{camera_info['quaternion'][0]}', '{camera_info['quaternion'][1]}', '{camera_info['quaternion'][2]}', '{camera_info['quaternion'][3]}');"
                cursor = connection.cursor()
                cursor.execute(command)
            
            
            connection.commit()

    def select_a_camera(self, drone_id, camera_face):
        '''
        Return : {
        translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z
        }
        '''
        command = f"SELECT * FROM camera_info WHERE drone_id ='{drone_id}' AND camera_face ='{camera_face};"
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            record_from_db = cursor.fetchall()

        result = []
        for row in record_from_db:
            result = [row['translation_x'], row['translation_y'], row['translation_z'], row['quaternion_w'], row['quaternion_x'], row['quaternion_y'], row['quaternion_z']]
        try:
            return result
        except Exception as e:
            return -1