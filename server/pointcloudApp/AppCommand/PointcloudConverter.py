from Tools.AirsimTools import AirsimTools
from DBController.SqliteDroneInfoTable import DroneInfoTable
from DBController.SqliteLidarInfoTable import LidarInfoTable
from DBController.SqliteCameraInfoTable import CameraInfoTable
from DBController.MysqlPointCloudInfoTable import MysqlPointCloudInfoTable
from scipy.spatial.transform import Rotation
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import time

class PointcloudConverter:
    def __init__(self):
        # pass
        self.color_dict = {}
        with open("seg_rgbs.txt", 'r') as file:
            for line in file:
                parts = line.strip().split('\t')
                self.color_dict[int(parts[0])] = eval(parts[1])
                
    def execute(self, parameters):
        """
        parameters : {
            'drone_name' : (Char)
            'drone_position' :['x_val', 'y_val', 'z_val'](NED) 
            'drone_quaternion' : ['w_val', 'x_val', 'y_val', 'z_val'](NED)
            },
            'point_cloud' : {
                'lidar_face' : (list)
            },
            'seg_info' : {
                'lidar_face' : (list)
            },
            'rgb_image' : {
                'camera_face' : (list)
            }
        }
        lidar_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        """
        start_time = time.time()
        drone_id = self.set_drone_info(parameters)
        self.start_save_point_cloud(parameters, drone_id)
        end_time = time.time()
        print(f"execute time: {end_time - start_time:.4f} seconds.")
        return {"status" : "ok", "message" : "save point cloud complete."}
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
        drone_position = parameters["drone_position"]
        drone_quaternion = parameters["drone_quaternion"]
        drone_quaternion = drone_quaternion[1:] + [drone_quaternion[0]]
        drone_rotation_matrix = Rotation.from_quat(drone_quaternion).as_matrix()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_lidar, lidar_face, parameters, drone_id, drone_rotation_matrix, drone_position) 
                    for lidar_face in parameters['point_cloud'].keys()]
            
            results = [future.result() for future in futures]

        total_point_cloud_info = np.concatenate([np.array(result[0]) for result in results], axis=0)
        total_color_info = np.concatenate([np.array(result[1]) for result in results], axis=0)

        total_point_cloud_info = total_point_cloud_info.tolist()
        total_color_info = total_color_info.tolist()

        MysqlPointCloudInfoTable().insert_point_clouds_with_color(total_point_cloud_info, total_color_info)

    def process_lidar(self, lidar_face, parameters, drone_id, drone_rotation_matrix, drone_position):
            point_cloud_list = parameters['point_cloud'][lidar_face]
            lidar_info = LidarInfoTable().select_a_lidar(drone_id, int(lidar_face))
            lidar_translation = lidar_info[:3]
            lidar_quaternion = lidar_info[3:]
            lidar_quaternion = [lidar_quaternion[1], lidar_quaternion[2], lidar_quaternion[3], lidar_quaternion[0]] 

            point_cloud_matrix = self.generate_point_cloud(point_cloud_list)
            point_cloud_matrix = point_cloud_matrix.transpose(2, 0, 1)

            total_rotate = np.dot(Rotation.from_quat(np.array(lidar_quaternion)).as_matrix(), drone_rotation_matrix)
            total_translate = np.array(lidar_translation) + np.array(drone_position)
            total_translate[1] = -total_translate[1]

            point_cloud_info = AirsimTools().relative2absolute_rotate(point_cloud_matrix, total_translate, total_rotate)
            point_cloud_info = np.round(point_cloud_info, 1)

            point_cloud_info = self.ned_to_enu(point_cloud_info).tolist()
            color_info = self.get_point_cloud_seg_color(parameters['seg_info'][lidar_face])
            # color_info = self.get_popint_cloud_color_info(lidar_face, point_cloud_list, parameters['rgb_image'][lidar_face])
            
            return point_cloud_info, color_info

    def generate_point_cloud(self, point_cloud_list):
        x = []
        y = []
        z = []
        for idx in range(0, len(point_cloud_list), 3):
            x += [point_cloud_list[idx]]
            y += [-point_cloud_list[idx+1]]
            z += [point_cloud_list[idx+2]]
        
        return np.dstack((np.array(x), np.array(y), np.array(z)))
    
    def get_point_cloud_seg_color(self, parameters):
        point_cloud_color_info = []
        for value in parameters:
            point_cloud_color_info += [self.color_dict[value]]
        
        return point_cloud_color_info

    def get_popint_cloud_color_info(self, camera_face, point_cloud_list, rgb_image):
        color_info = []

        height, width = 540, 960
        rgb_image_ary = np.array(rgb_image).reshape((height, width, 3))

        for i in range(0, len(point_cloud_list), 3):
            x, y, z = point_cloud_list[i], point_cloud_list[i+1], point_cloud_list[i+2]

            principal_point_x = width / 2
            principal_point_y = height / 2

            u = int((x / z) + principal_point_x)
            v = int((y / z) + principal_point_y)

            if 0 <= u < width and 0 <= v < height:
                # get rgb
                color = rgb_image_ary[v, u, :].tolist()  # get color on (u, v)
            else:
                # if the pixel (u, v) not in range, set the color to [255, 255, 255]
                color = [255, 255, 255]
            
            color_info.append(color)
        
        return color_info

        

    def ned_to_enu(self, point_cloud_array):
        enu_point_cloud_array = np.empty_like(point_cloud_array)
        enu_point_cloud_array[:, 0] = point_cloud_array[:, 1]
        enu_point_cloud_array[:, 1] = -point_cloud_array[:, 2]
        enu_point_cloud_array[:, 2] = point_cloud_array[:, 0]

        return enu_point_cloud_array