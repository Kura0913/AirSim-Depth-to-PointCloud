import math
import numpy as np
import airsim
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.ColorInfoTable import ColorInfoTable
from DBController.CameraInfoTable import CameraInfoTable
from scipy.spatial.transform import Rotation

MIN_DEPTH_METERS = 0
MAX_DEPTH_METERS = 100

class SavePointCloud:
    def __init__(self):
        self.fov = 90
        self.width = 960
        self.height = 540
        self.fx = self.width / (2 * math.tan(self.fov * math.pi / 360))
        self.fy = self.fx
        # self.fy = self.height / ( 2 * math.tan(self.fov / 2))
        self.cx = self.width / 2
        self.cy = self.height / 2

    def execute(self, parameters):
        '''
        parameters : {
            'drone_name' : (Char)
            'drone_position' : {'x_val', 'y_val', 'z_val'} (NED)
            'drone_quaternion' : {'w_val', 'x_val', 'y_val', 'z_val'}
            'depth_image' : {
                'camera_face' : {
                    id : pixel_value(float)
                }
            'rgb_image' : {
                'camera_face' : {
                    id : pixel_value(float)
                }
            }
        }

        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        '''
        drone_id = self.set_drone_info(parameters)

        self.start_save_point_cloud(parameters, drone_id)

        return {"status" : "ok", "message" : "save point cloud complete."}
        try:
            drone_id = self.set_drone_info(parameters)

            self.start_save_point_cloud(parameters, drone_id)

            return {"status" : "ok", "message" : "save point cloud complete."}
        except Exception as e:
            return{"status" : "fail", "message" : "save point cloud failed, please check the previously sent parameters.", "exception" : str(e)}
    
    def set_drone_info(self, parameters):
        drone_info = DroneInfoTable().select_a_drone(parameters['drone_name'])
        self.fov = drone_info[1]
        self.width = drone_info[2]
        self.height = drone_info[3]
        self.fx = self.width / (2 * math.tan(self.fov * math.pi / 360))
        self.fy = self.fx
        # self.fy = self.height / ( 2 * math.tan(self.fov / 2))
        self.cx = self.width / 2
        self.cy = self.height / 2

        return drone_info[0]
    
    def start_save_point_cloud(self, parameters, drone_id):
        point_cloud_list = []
        drone_position = []
        drone_quaternion = []
        # format position info to list
        for _, value in parameters['drone_position'].items():
            drone_position = drone_position + [value]
        # format quaternion info to list
        for _, value in parameters['drone_quaternion'].items():
            drone_quaternion = drone_quaternion + [value]
        drone_quaternion = [drone_quaternion[1], drone_quaternion[2], drone_quaternion[3], drone_quaternion[0]] # format quaternion to [x_val, y_val, z_val, w_val]
        drone_position = AirsimTools().ned2cartesian(drone_position[0], drone_position[1], drone_position[2]) # cartesian coordinate system
        

        ### Intrinsic parameters matrix
        k = np.array([
            [self.fx, 0, self.cx, 0],
            [0, self.fy, self.cy, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        for camera_face, depth_image in parameters["depth_image"].items():
            # convert dict to list
            depth_image_ary_1d = [depth_image[index] for index in depth_image.keys()]
            camera_info = CameraInfoTable().select_a_camera(drone_id, int(camera_face))
            camera_translate = [camera_info[0], camera_info[1], camera_info[2]]
            camera_quaternion = [camera_info[4], camera_info[5], camera_info[6], camera_info[3]]

            depth_image_ary_1d = np.array(depth_image_ary_1d, dtype=np.float)
            depth_image_ary_1d[depth_image_ary_1d > 255] = 255

            depth_image_ary_2d = np.reshape(depth_image_ary_1d, (self.height, self.width))
            depth_image_ary_2d_converted = AirsimTools().depth_conversion(depth_image_ary_2d, self.fx)
            cloud_point_matrix, valid_mask = self.generate_point_cloud(depth_image_ary_2d_converted)
            cloud_point_matrix = cloud_point_matrix.transpose(2, 0, 1)

            total_rotate = np.dot(Rotation.from_quat(np.array(drone_quaternion)).as_matrix(), Rotation.from_quat(np.array(camera_quaternion)).as_matrix())
            total_translate = np.dot(Rotation.from_quat(np.array(drone_quaternion)).as_matrix(), np.array(camera_translate)) + np.array(drone_position)

            point_cloud_info = AirsimTools().relative2absolute_rotate(cloud_point_matrix, total_translate, total_rotate)

            # cloud_point_matrix_converted = AirsimTools().relative2absolute(cloud_point_matrix, np.array(camera_translate), np.array(camera_quaternion), False)
            # point_cloud_info = AirsimTools().relative2absolute(cloud_point_matrix_converted, np.array(drone_position), np.array(drone_quaternion))
            
            point_cloud_info = np.round(point_cloud_info, 2)
            point_cloud_info = point_cloud_info[valid_mask.reshape(-1)]

            point_cloud_info = point_cloud_info.tolist()
            point_cloud_list = point_cloud_list + point_cloud_info

        PointCloudInfoTable().insert_point_clouds(point_cloud_list)

    def generate_point_cloud(self, depth):
        rows, cols = depth.shape
        c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
        valid = (depth > 0) & (depth < 255)
        z = 1000 * np.where(valid, depth / 256.0, np.nan) # convert z to meters
        x = np.where(valid, z * (c - self.cx) / self.fx, 0)
        y = np.where(valid, z * (r - self.cy) / self.fy, 0)
        return np.dstack((x, -y, -z)), valid
    