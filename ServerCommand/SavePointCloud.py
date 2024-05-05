import math
import numpy as np
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.ColorInfoTable import ColorInfoTable
from DBController.CameraInfoTable import CameraInfoTable

class SavePointCloud:
    def __init__(self):
        self.fov = 90
        self.width = 1920
        self.height = 1080
        self.fx = self.width / ( 2 * math.tan(self.fov / 2))
        self.fy = self.height / ( 2 * math.tan(self.fov / 2))
        self.cx = self.width / 2
        self.cy = self.height / 2

    def execute(self, parameters):
        '''
        parameters : {
            drone_name : (Char)
            drone_position : [x_val, y_val, z_val] (NED)
            drone_quaternion : [w_val, x_val, y_val, z_val]
            depth_image : {camera_face : image_array}
            rgb_image : {camera_face : image_array}
        }

        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        '''
        try:
            drone_id = self.set_drone_info(parameters)

            self.start_save_point_cloud(self, parameters, drone_id)

            return {"status" : "ok", "message" : "save point cloud complete."}
        except:
            return{"status" : "fail", "message" : "save point cloud failed, please check the previously sent parameters.", "parameters" : parameters}
    
    def set_drone_info(self, parameters):
        drone_info = DroneInfoTable.select_a_drone(parameters['drone_name'])
        self.fov = drone_info[0]
        self.width = drone_info[1]
        self.height = drone_info[2]
        self.fx = self.width / ( 2 * math.tan(self.fov / 2))
        self.fy = self.height / ( 2 * math.tan(self.fov / 2))
        self.cx = self.width / 2
        self.cy = self.height / 2

        return drone_info[0]
    
    def start_save_point_cloud(self, parameters, drone_id):
        point_cloud_list = []

        drone_position = AirsimTools.ned2cartesian(parameters['drone_position'][0], parameters['drone_position'][1], parameters['drone_position'][2]) # cartesian coordinate system
        drone_quaternion = [parameters['drone_quaternion'][0], parameters['drone_quaternion'][1], parameters['drone_quaternion'][2], parameters['drone_quaternion'][3]]

        ### Intrinsic parameters matrix
        k = np.array([
            [self.fx, 0, self.cx, 0],
            [0, self.fy, self.cy, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        for camera_face, depth_image in parameters["depth_image"]:
            camera_info = CameraInfoTable.select_a_camera(drone_id, int(camera_face))

        
            ### Extrinsic Parameters
            # translation matrix
            t = np.array([[camera_info[0]], [camera_info[1]], [camera_info[2]]])
            # rotate matrix
            r = AirsimTools.quaternion2ratate(np.array([camera_info[3], camera_info[4], camera_info[5], camera_info[6]]))
            
            r_T = np.hstack((r, t))
            r_T = np.vstack((r_T, np.array([0, 0, 0, 1])))    
            
            for u in range(self.width):
                for v in range(self.height):
                    z = depth_image[u, v]/1000 # divide by 1000 to convert z to meters
                    # limit the range in 0 to 30 of saved point cloud
                    if z == 0 or z > 30:
                        continue
                    
                    pixel_matrix = np.array([[u], [v], [1], [1/z]]) # set pixel matrix

                    camera_matrix = k.dot(r_T)
                    camera_matrix_inv = np.linalg.inv(camera_matrix) # get inverse camera matrix
                    point_cloud_matrix = z * camera_matrix_inv.dot(pixel_matrix)
                    point_cloud_info = [point_cloud_matrix[0], point_cloud_matrix[1], point_cloud_matrix[2]] # relative position
                    # convert relative position to abs position
                    point_cloud_info = AirsimTools.relative2absolute(point_cloud_info, drone_position, drone_quaternion)
                    if point_cloud_info not in point_cloud_list:
                        point_cloud_list.append(point_cloud_info)

        PointCloudInfoTable.insert_point_clouds(point_cloud_list)