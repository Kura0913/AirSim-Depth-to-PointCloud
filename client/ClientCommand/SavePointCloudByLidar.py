import airsim
from ClientObject.ClientCameraSensorData import ClientCameraSensorData
import time

class SavePointCloudByLidar:
    def __init__(self):
        self.lidar_dict = {
            0:"front_lidar",
            1:"back_lidar",
            2:"right_lidar",
            3:"left_lidar",
            4:"up_lidar",
            5:"down_lidar"
        }        

    def execute(self, airsim_client:airsim.MultirotorClient, drone_name, client_camera_sensor_data:ClientCameraSensorData):
        '''
        lidar_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        ----------------------------------------------
        Return : {
            'drone_name' : (Char)
            'drone_position' :['x_val', 'y_val', 'z_val'](NED) 
            'drone_quaternion' : ['w_val', 'x_val', 'y_val', 'z_val'](NED)
            } 
            'point_cloud' : {
                'lidar_face' : {
                    id : pixel_value(float)
                }
            'seg_info' : {
                'lidar_face' : {
                    id : pixel_value(float)
                }
            }
        }
        '''
        
        parameters = {
            "drone_name":drone_name
        }
        drone_pose = airsim_client.simGetVehiclePose(drone_name)
        start_time = time.time()
        parameters = self.get_lidar_data(airsim_client, drone_name, client_camera_sensor_data.lidar_list, parameters)
        end_time = time.time()
        print(f"execute time: {end_time - start_time:.4f} seconds.")
        parameters["drone_position"] = [drone_pose.position.x_val, drone_pose.position.y_val, drone_pose.position.z_val]
        parameters["drone_quaternion"] = [drone_pose.orientation.w_val, drone_pose.orientation.x_val, drone_pose.orientation.y_val, drone_pose.orientation.z_val]
        
        return parameters

    def get_lidar_data(self, airsim_client:airsim.MultirotorClient, drone_name, lidar_list, parameters = {}):
        parameters['point_cloud'] = {}
        parameters["seg_info"] = {}
        
        for lidar_face in lidar_list:
            lidar_data = airsim_client.getLidarData(self.lidar_dict[lidar_face], drone_name)
            parameters["point_cloud"][lidar_face] = lidar_data.point_cloud
            parameters["seg_info"][lidar_face] = lidar_data.segmentation

        return parameters