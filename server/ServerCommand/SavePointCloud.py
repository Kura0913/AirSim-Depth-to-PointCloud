import math
import numpy as np
import airsim
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.ColorInfoTable import ColorInfoTable
from DBController.CameraInfoTable import CameraInfoTable

MIN_DEPTH_METERS = 0
MAX_DEPTH_METERS = 100

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
        self.fx = self.width / ( 2 * math.tan(self.fov / 2))
        self.fy = self.height / ( 2 * math.tan(self.fov / 2))
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
            depth_image_ary = [depth_image[index] for index in sorted(depth_image.keys())]
            camera_info = CameraInfoTable().select_a_camera(drone_id, int(camera_face))

            depth_image_ary = airsim.list_to_2d_float_array(depth_image_ary, self.width, self.height)
            depth_image_ary = depth_image_ary.reshape(self.height, self.width)
            depth_image_ary = depth_image_ary * 1000
            depth_image_ary = np.clip(depth_image_ary, 0, 65535) # millimeters


            ### Extrinsic Parameters
            # translation matrix
            t = np.array([[camera_info[0]], [camera_info[1]], [camera_info[2]]])
            # rotate matrix
            r = AirsimTools().quaternion2ratate(np.array([camera_info[3], camera_info[4], camera_info[5], camera_info[6]]))
            
            r_T = np.hstack((r, t))
            r_T = np.vstack((r_T, np.array([0, 0, 0, 1])))    
            
            u, v = np.meshgrid(np.arange(depth_image_ary.shape[0]), np.arange(depth_image_ary.shape[1]), indexing='ij')
            z = depth_image_ary / 1000 # divide by 1000 to convert z to meters
            
            valid_mask = np.logical_and(z != 0, z <= 30) # only save the depth in 0 to 30 meter
            
            pixel_matrix = np.stack([u, v, np.ones_like(u), 1 / z], axis=-1)  # get pixel matrix
            camera_matrix = np.dot(k, r_T) # get camera matrix
            camera_matrix_inv = np.linalg.inv(camera_matrix)
            pixel_matrix = pixel_matrix.transpose(2, 0, 1)
            point_cloud_matrix = np.zeros((4, depth_image_ary.shape[0], depth_image_ary.shape[1]))  # 初始化點雲矩陣
            for i in range(depth_image_ary.shape[0]):
                for j in range(depth_image_ary.shape[1]):
                    pixel_matrix_ij = pixel_matrix[:, i, j]  # 獲取當前像素位置的 4 維向量
                    point_cloud_matrix[:, i, j] = z[i, j] * np.matmul(camera_matrix_inv, pixel_matrix_ij)

            point_cloud_info = AirsimTools().relative2absolute(point_cloud_matrix, drone_position, drone_quaternion)
            point_cloud_info = point_cloud_info[valid_mask.reshape(-1)]

            

            # for u in range(self.width):
            #     for v in range(self.height):
            #         print(f"pixel:{u}, {v}")
            #         z = depth_image_ary[u, v]/1000 # divide by 1000 to convert z to meters
            #         # limit the range in 0 to 30 of saved point cloud
            #         if z == 0 or z > 30:
            #             continue
                    
            #         pixel_matrix = np.array([[u], [v], [1], [1/z]], dtype=object) # set pixel matrix

            #         camera_matrix = k.dot(r_T)
            #         camera_matrix_inv = np.linalg.inv(camera_matrix) # get inverse camera matrix
            #         point_cloud_matrix = z * camera_matrix_inv.dot(pixel_matrix)
            #         point_cloud_info = [point_cloud_matrix[0,0], point_cloud_matrix[1,0], point_cloud_matrix[2,0]] # relative position
            #         # convert relative position to abs position
            #         point_cloud_info = AirsimTools().relative2absolute(point_cloud_info, drone_position, drone_quaternion)
            #         if point_cloud_info not in point_cloud_list and PointCloudInfoTable().select_a_point(point_cloud_info) <= 0:
            #             point_cloud_list = point_cloud_list + [point_cloud_info]

        PointCloudInfoTable().insert_point_clouds(point_cloud_list)