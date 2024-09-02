from DBController.DroneInfoTable import DroneInfoTable
from DBController.CameraInfoTable import CameraInfoTable
from DBController.LidarInfoTable import LidarInfoTable
import time

class GetInitialInfo:
    def __init__(self):
        pass
    def execute(self, parameters):
        '''
        parameters : {
            drone_name: (str),
            camera:{
                camera_face : {
                    translation: (list),
                    quaternion: (list),
                    fov,
                    width,
                    height,
                }            
            },
            lidar:{
                lidar_face:{
                    translation: (list),
                    quaternion: (list)
                }
            }
        }
        '''
        start_time = time.time()
        if len(DroneInfoTable().select_a_drone(parameters["drone_name"])) <= 0:
            DroneInfoTable().insert_a_drone(parameters["drone_name"])
            print(f"Drone: {parameters['drone_name']} info save success!!")
        drone_id_list = DroneInfoTable().select_a_drone(parameters["drone_name"])
        print(drone_id_list)
        drone_id = drone_id_list[0]

        self.get_camera_info(parameters["camera"], drone_id)
        self.get_lidar_info(parameters["lidar"], drone_id)
        end_time = time.time()
        print(f"execute time: {end_time - start_time:.4f} seconds.")
        result_message = {"status" : "ok", "message" : "Initial settings completed."}

        return result_message
    
    def get_camera_info(self, parameters, drone_id):
        camera_dict = {}
        for camera_face, camera_info in parameters.items():
            if len(CameraInfoTable().select_a_camera(drone_id, camera_face)) <= 0:
                camera_dict[camera_face] = {}
                camera_dict[camera_face]["drone_id"] = drone_id
                camera_dict[camera_face]["translation"] = camera_info['translation']
                camera_dict[camera_face]["quaternion"] = camera_info['quaternion']
                camera_dict[camera_face]["fov"] = camera_info['fov']
                camera_dict[camera_face]["width"] = camera_info['width']
                camera_dict[camera_face]["height"] = camera_info['height']
                
        CameraInfoTable().insert_cameras(camera_dict)

    def get_lidar_info(self, parameters, drone_id):
        lidar_dict = {}
        for lidar_face, lidar_info in parameters.items():
            if len(LidarInfoTable().select_a_lidar(drone_id, lidar_face)) <= 0:
                lidar_dict[lidar_face] = {}
                lidar_dict[lidar_face]["drone_id"] = drone_id
                lidar_dict[lidar_face]["translation"] = lidar_info['translation']
                lidar_dict[lidar_face]["quaternion"] = lidar_info['quaternion']
                
        LidarInfoTable().insert_lidars(lidar_dict)