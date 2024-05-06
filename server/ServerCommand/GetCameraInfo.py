from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.ColorInfoTable import ColorInfoTable
from DBController.CameraInfoTable import CameraInfoTable

class GetCameraInfo:
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
                    translation_x,
                    translation_y,
                    translation_z,
                    quaternion_w,
                    quaternion_x,
                    quaternion_y,
                    quaternion_z
                }
            }
        }
        '''

        if len(DroneInfoTable.select_a_drone(parameters["drone_name"])) <= 0:
            DroneInfoTable.insert_a_drone(parameters["drone_name"], parameters["fov"], parameters["width"], parameters["height"])
        drone_id = DroneInfoTable.select_a_drone(parameters["drone_name"])[0]
        camera_dict = {}
        for camera_face, camera_info in parameters["camera"].items():
            camera_info_list = [] # [translation_x, translation_y, translation_z, quaternion_w, quaternion_x, quaternion_y, quaternion_z]
            for _, value in camera_info.items():
                camera_info_list.append(value)
            
            if len(CameraInfoTable.select_a_camera(drone_id, camera_face)) <= 0:
                camera_dict[camera_face] = {}
                camera_dict[camera_face]["drone_id"] = drone_id
                camera_dict[camera_face]["translation"] = camera_info_list[:3]
                camera_dict[camera_face]["quaternion"] = camera_info_list[3:]
                
        CameraInfoTable.insert_a_camera(drone_id, camera_dict)
        result_message = {"status" : "ok", "message" : "Initial settings completed."}

        return result_message