from DBController.DroneInfoTable import DroneInfoTable
from DBController.CameraInfoTable import CameraInfoTable
from DBController.LidarInfoTable import LidarInfoTable
from Tools.AirsimTools import AirsimTools

class GetInitialInfo:
    def __init__(self):
        pass
    def execute(self, parameters):
        '''
        parameters : {
            drone_name,
            fov,
            width,
            height,
            camera:{
                camera_face : {
                    translation_x:float,
                    translation_y:float,
                    translation_z:float,
                    quaternion_w:float,
                    quaternion_x:float,
                    quaternion_y:float,
                    quaternion_z:float
                }            
            },
            lidar:{
                lidar_face:{
                    translation_x:float,
                    translation_y:float,
                    translation_z:float,
                    quaternion_w:float,
                    quaternion_x:float,
                    quaternion_y:float,
                    quaternion_z:float
                }
            }
        }
        '''

        if len(DroneInfoTable().select_a_drone(parameters["drone_name"])) <= 0:
            DroneInfoTable().insert_a_drone(parameters["drone_name"], parameters["fov"], parameters["width"], parameters["height"])
            print(f"Drone: {parameters['drone_name']} info save success!!")
        print(DroneInfoTable().select_a_drone(parameters["drone_name"]))
        drone_id = DroneInfoTable().select_a_drone(parameters["drone_name"])[0]

        self.get_camera_info(parameters["camera"], drone_id)
        self.get_lidar_info(parameters["lidar"], drone_id)

        result_message = {"status" : "ok", "message" : "Initial settings completed."}

        return result_message
    
    def get_camera_info(self, parameters, drone_id):
        camera_dict = {}
        for camera_face, camera_info in parameters.items():
            camera_info_list = [] # [translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z]
            for _, value in camera_info.items():
                camera_info_list.append(value)
            
            if len(CameraInfoTable().select_a_camera(drone_id, camera_face)) <= 0:
                camera_dict[camera_face] = {}
                camera_dict[camera_face]["drone_id"] = drone_id
                camera_dict[camera_face]["translation"] = camera_info_list[:3]
                camera_dict[camera_face]["quaternion"] = camera_info_list[3:]
                
        CameraInfoTable().insert_cameras(camera_dict)

    def get_lidar_info(self, parameters, drone_id):
        lidar_dict = {}
        for lidar_face, lidar_info in parameters.items():
            lidar_info_list = [] # [translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z]
            for _, value in lidar_info.items():
                lidar_info_list.append(value)
            
            if len(CameraInfoTable().select_a_camera(drone_id, lidar_face)) <= 0:
                lidar_dict[lidar_face] = {}
                lidar_dict[lidar_face]["drone_id"] = drone_id
                lidar_dict[lidar_face]["translation"] = lidar_info_list[:3]
                lidar_dict[lidar_face]["quaternion"] = lidar_info_list[3:]
                
        LidarInfoTable().insert_lidars(lidar_dict)