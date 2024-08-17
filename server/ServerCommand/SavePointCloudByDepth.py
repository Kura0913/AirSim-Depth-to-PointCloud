import math
import numpy as np
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.CameraInfoTable import CameraInfoTable
from scipy.spatial.transform import Rotation
import time

MIN_DEPTH_METERS = 0
MAX_DEPTH_METERS = 100
LIMIT_DEPTH = 50

class SavePointCloudByDepth:
    def __init__(self):
        self.fov = 90
        self.width = 960
        self.height = 540
        self.fx = self.width / (2 * math.tan(self.fov * math.pi / 360))
        self.fy = self.fx
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
                    id : pixel_value
                }
            'rgb_image' : {
                'camera_face' : {
                    id : pixel_value
                }
            }
        }

        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        '''
        start_time = time.time()
        try:
            drone_id = self.set_drone_info(parameters)

            self.start_save_point_cloud(parameters, drone_id)
            end_time = time.time()
            print(f"execute time: {end_time - start_time:.4f} seconds.")
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
        self.cx = self.width / 2
        self.cy = self.height / 2

        return drone_info[0]
    
    def start_save_point_cloud(self, parameters, drone_id):
        total_point_cloud_info = []
        drone_position = []
        drone_quaternion = []
        # format position info to list
        for _, value in parameters['drone_position'].items():
            drone_position = drone_position + [value]
        # format quaternion info to list
        for _, value in parameters['drone_quaternion'].items():
            drone_quaternion = drone_quaternion + [value]
        drone_quaternion = [drone_quaternion[1], drone_quaternion[2], drone_quaternion[3], drone_quaternion[0]] # format quaternion to [x_val, y_val, z_val, w_val]

        for camera_face, depth_image in parameters["depth_image"].items():
            # convert dict to list
            depth_image_ary_1d = [depth_image[index] for index in depth_image.keys()]
            camera_info = CameraInfoTable().select_a_camera(drone_id, int(camera_face))
            camera_translate = [camera_info[0], camera_info[1], camera_info[2]]
            camera_quaternion = [camera_info[4], camera_info[5], camera_info[6], camera_info[3]]

            depth_image_ary_1d = np.array(depth_image_ary_1d, dtype=np.float)
            depth_image_ary_1d[depth_image_ary_1d > LIMIT_DEPTH] = 255 # meter = value * 1000 / 1024, value = meter * 1024 / 1000

            depth_image_ary_2d = np.reshape(depth_image_ary_1d, (self.height, self.width))
            depth_image_ary_2d_converted = AirsimTools().depth_conversion(depth_image_ary_2d, self.fx)
            point_cloud_matrix, valid_mask = self.generate_point_cloud(depth_image_ary_2d_converted)
            point_cloud_matrix = point_cloud_matrix.transpose(2, 0, 1)

            total_rotate = np.dot(Rotation.from_quat(np.array(camera_quaternion)).as_matrix(), Rotation.from_quat(np.array(drone_quaternion)).as_matrix())
            total_translate = np.array(camera_translate) + np.array(drone_position)
            total_translate[1] = -total_translate[1]

            point_cloud_info = AirsimTools().relative2absolute_rotate(point_cloud_matrix, total_translate, total_rotate)

            point_cloud_info = np.round(point_cloud_info, 2)
            point_cloud_info = point_cloud_info[valid_mask.reshape(-1)]

            point_cloud_info = self.ned_to_enu(point_cloud_info).tolist()
            total_point_cloud_info = total_point_cloud_info + point_cloud_info

        PointCloudInfoTable().insert_point_clouds(total_point_cloud_info)

    def generate_point_cloud(self, depth):
        rows, cols = depth.shape
        c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
        valid = (depth > 0) & (depth < LIMIT_DEPTH)
        z = 1000 * np.where(valid, depth / 1000, np.nan)
        x = np.where(valid, z * (c - self.cx) / self.fx, 0)
        y = np.where(valid, z * (r - self.cy) / self.fy, 0)

        return np.dstack((z, -x, y)), valid
    
    def ned_to_enu(self, point_cloud_array):
        enu_point_cloud_array = np.empty_like(point_cloud_array)
        enu_point_cloud_array[:, 0] = point_cloud_array[:, 1]
        enu_point_cloud_array[:, 1] = -point_cloud_array[:, 2]
        enu_point_cloud_array[:, 2] = point_cloud_array[:, 0]

        return enu_point_cloud_array