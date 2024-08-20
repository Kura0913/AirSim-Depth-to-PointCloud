import numpy as np
import time
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.LidarInfoTable import LidarInfoTable
from DBController.MongoDBPointCloudTable import MongoDBPointCloudTable
from scipy.spatial.transform import Rotation
from concurrent.futures import ThreadPoolExecutor

class SavePointCloudByLidar:
    def __init__(self):
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
            } 
            'point_cloud' : {
                'lidar_face' : (list)
            'seg_info' : {
                'lidar_face' : (list)
            }
        }
        lidar_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        """
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
        def process_lidar_face(lidar_face, point_cloud_list, parameters, drone_id, drone_rotation_matrix, drone_position):
            # 放入目前在迴圈內的處理邏輯
            lidar_info = LidarInfoTable().select_a_lidar(drone_id, int(lidar_face))
            lidar_translation = lidar_info[:3]
            lidar_quaternion = lidar_info[3:]
            lidar_quaternion = [lidar_quaternion[1], lidar_quaternion[2], lidar_quaternion[3], lidar_quaternion[0]] 

            color_info = self.get_point_cloud_color(parameters['seg_info'][lidar_face]) 

            point_cloud_matrix = self.generate_point_cloud(point_cloud_list)
            point_cloud_matrix = point_cloud_matrix.transpose(2, 0, 1)

            total_rotate = np.dot(Rotation.from_quat(np.array(lidar_quaternion)).as_matrix(), drone_rotation_matrix)
            total_translate = np.array(lidar_translation) + np.array(drone_position)
            total_translate[1] = -total_translate[1]

            point_cloud_info = AirsimTools().relative2absolute_rotate(point_cloud_matrix, total_translate, total_rotate)
            point_cloud_info = np.round(point_cloud_info, 2)

            point_cloud_info = self.ned_to_enu(point_cloud_info).tolist()
            
            return point_cloud_info, color_info

        total_point_cloud_info = []
        total_color_info = []
        drone_position = parameters["drone_position"]
        drone_quaternion = parameters["drone_quaternion"]
        drone_quaternion = drone_quaternion[1:] + [drone_quaternion[0]]
        drone_rotation_matrix = Rotation.from_quat(drone_quaternion).as_matrix()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_lidar_face, lidar_face, point_cloud_dict, parameters, drone_id, drone_rotation_matrix, drone_position) 
                    for lidar_face, point_cloud_dict in parameters['point_cloud'].items()]
            
            results = [future.result() for future in futures]

        total_point_cloud_info = np.concatenate([np.array(result[0]) for result in results], axis=0)
        total_color_info = np.concatenate([np.array(result[1]) for result in results], axis=0)

        total_point_cloud_info = total_point_cloud_info.tolist()
        total_color_info = total_color_info.tolist()

        # for lidar_face, point_cloud_dict in parameters['point_cloud'].items():
        #     lidar_info = LidarInfoTable().select_a_lidar(drone_id, int(lidar_face))
        #     lidar_translation = lidar_info[:3]
        #     lidar_quaternion = lidar_info[3:]
        #     lidar_quaternion = [lidar_quaternion[1], lidar_quaternion[2], lidar_quaternion[3], lidar_quaternion[0]] # format quaternion to [x_val, y_val, z_val, w_val]

        #     ori_point_cloud_list = [point_cloud_dict[str(idx)] for idx in range(len(point_cloud_dict))]
        #     color_info = self.get_point_cloud_color(parameters['seg_info'][lidar_face]) 

        #     point_cloud_matrix = self.generate_point_cloud(ori_point_cloud_list)
        #     point_cloud_matrix = point_cloud_matrix.transpose(2, 0, 1)

        #     total_rotate = np.dot(Rotation.from_quat(np.array(lidar_quaternion)).as_matrix(), drone_rotation_matrix)
        #     total_translate = np.array(lidar_translation) + np.array(drone_position)
        #     total_translate[1] = -total_translate[1]

        #     point_cloud_info = AirsimTools().relative2absolute_rotate(point_cloud_matrix, total_translate, total_rotate)
        #     point_cloud_info = np.round(point_cloud_info, 2)

        #     point_cloud_info = self.ned_to_enu(point_cloud_info).tolist()
        #     total_point_cloud_info += point_cloud_info
        #     total_color_info += color_info

        # PointCloudInfoTable().insert_point_clouds(total_point_cloud_info)
        # PointCloudInfoTable().insert_point_clouds_with_color(total_point_cloud_info, total_color_info)        
        MongoDBPointCloudTable().Insert_point_clouds_with_color(total_point_cloud_info, total_color_info)

    def generate_point_cloud(self, point_cloud_list):
        x = []
        y = []
        z = []
        for idx in range(0, len(point_cloud_list), 3):
            x += [point_cloud_list[idx]]
            y += [-point_cloud_list[idx+1]]
            z += [point_cloud_list[idx+2]]
        
        return np.dstack((np.array(x), np.array(y), np.array(z)))
    
    def get_point_cloud_color(self, parameters):
        point_cloud_color_info = []
        for value in parameters:
            point_cloud_color_info += [self.color_dict[value]]
        
        return point_cloud_color_info

    def ned_to_enu(self, point_cloud_array):
        enu_point_cloud_array = np.empty_like(point_cloud_array)
        enu_point_cloud_array[:, 0] = point_cloud_array[:, 1]
        enu_point_cloud_array[:, 1] = -point_cloud_array[:, 2]
        enu_point_cloud_array[:, 2] = point_cloud_array[:, 0]

        return enu_point_cloud_array