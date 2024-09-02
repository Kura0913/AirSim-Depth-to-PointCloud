from Tools.AirsimTools import AirsimTools
from DBController.SqliteDroneInfoTable import DroneInfoTable
from DBController.SqliteCameraInfoTable import CameraInfoTable
from DBController.MysqlPointCloudInfoTable import MysqlPointCloudInfoTable
from scipy.spatial.transform import Rotation
from concurrent.futures import ThreadPoolExecutor
import time
import math
import numpy as np

MIN_DEPTH_METERS = 0
MAX_DEPTH_METERS = 100
LIMIT_DEPTH = 50

class DepthConverter:
    def __init__(self):
        pass

    def execute(self, parameters):
        '''
        parameters : {
            'drone_name' : (Char)
            'drone_position' :['x_val', 'y_val', 'z_val'](NED) 
            'drone_quaternion' : ['w_val', 'x_val', 'y_val', 'z_val'](NED)
            'depth_image' : {
                'camera_face' : (list)
            'rgb_image' : {
                'camera_face' : (list)
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

        return drone_info[0]
    
    def start_save_point_cloud(self, parameters, drone_id):
        total_point_cloud_info = []
        total_color_info = []

        drone_position = parameters['drone_position']
        drone_quaternion = parameters['drone_quaternion']
        drone_quaternion = drone_quaternion[1:] + [drone_quaternion[0]]
        drone_rotation_matrix = Rotation.from_quat(drone_quaternion).as_matrix()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_camera, camera_face, parameters, drone_id, drone_position, drone_rotation_matrix) 
                       for camera_face in parameters["depth_image"].keys()]

            for future in futures:
                point_cloud_info, color_info = future.result()
                if point_cloud_info:
                    total_point_cloud_info.extend(point_cloud_info)
                if color_info:
                    total_color_info.extend(color_info)

        MysqlPointCloudInfoTable().insert_point_clouds_with_color(total_point_cloud_info, total_color_info)

    def process_camera(self, camera_face, parameters, drone_id, drone_position, drone_rotation_matrix):
        camera_info_dict = CameraInfoTable().select_a_camera(drone_id, int(camera_face))
        fx = camera_info_dict['width'] / (2 * math.tan(camera_info_dict['fov'] * math.pi / 360))

        depth_image_ary_1d = parameters['depth_image'][camera_face]
        rgb_image = parameters["rgb_image"][camera_face]
        depth_image_ary_1d[depth_image_ary_1d > LIMIT_DEPTH] = 255

        depth_image_ary_2d = np.reshape(depth_image_ary_1d, (camera_info_dict['hieght'], camera_info_dict['width']))
        depth_image_ary_2d_converted = AirsimTools().depth_conversion(depth_image_ary_2d, fx)
        point_cloud_matrix, valid_mask = self.generate_point_cloud(depth_image_ary_2d_converted, camera_info_dict)
        point_cloud_matrix = point_cloud_matrix.transpose(2, 0, 1)

        

        total_rotate = np.dot(Rotation.from_quat(np.array(camera_info_dict['quaternion'])).as_matrix(), drone_rotation_matrix)
        total_translate = np.array(camera_info_dict['translation']) + np.array(drone_position)
        total_translate[1] = -total_translate[1]

        point_cloud_info = AirsimTools().relative2absolute_rotate(point_cloud_matrix, total_translate, total_rotate)

        point_cloud_info = np.round(point_cloud_info, 2)
        point_cloud_info = point_cloud_info[valid_mask.reshape(-1)]

        color_info = self.get_point_cloud_color(rgb_image, valid_mask, camera_info_dict)

        point_cloud_info = self.ned_to_enu(point_cloud_info).tolist()
        return point_cloud_info, color_info

    def get_point_cloud_color(self, rgb_image, valid_mask, camera_info_dict):
        rgb_array = np.array(rgb_image).reshape(camera_info_dict['height'], camera_info_dict['width'], 3)
        valid_colors = rgb_array[valid_mask]
        return valid_colors.reshape(-1, 3)

    def generate_point_cloud(self, depth, camera_info_dict):
        cx = camera_info_dict['width'] / 2
        cy = camera_info_dict['height'] / 2
        fx = camera_info_dict['width'] / (2 * math.tan(camera_info_dict['fov'] * math.pi / 360))
        fy = fx

        rows, cols = depth.shape
        c, r = np.meshgrid(np.arange(cols), np.arange(rows), sparse=True)
        valid = (depth > 0) & (depth < LIMIT_DEPTH)
        z = 1000 * np.where(valid, depth / 1000, np.nan)
        x = np.where(valid, z * (c - cx) / fx, 0)
        y = np.where(valid, z * (r - cy) / fy, 0)

        return np.dstack((z, -x, y)), valid
    
    def ned_to_enu(self, point_cloud_array):
        enu_point_cloud_array = np.empty_like(point_cloud_array)
        enu_point_cloud_array[:, 0] = point_cloud_array[:, 1]
        enu_point_cloud_array[:, 1] = -point_cloud_array[:, 2]
        enu_point_cloud_array[:, 2] = point_cloud_array[:, 0]

        return enu_point_cloud_array