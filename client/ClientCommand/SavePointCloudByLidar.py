import airsim
from ThreadController.AirSimTaskThread import AirSimTaskThread
from ClientObject.ClientCameraSensorData import ClientCameraSensorData

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
            'lidar_position' : {
                'lidar_face':{'x_val', 'y_val', 'z_val'}(NED)
            } 
            'lidar_quaternion' : {
                'lidar_face':{'w_val', 'x_val', 'y_val', 'z_val'}(NED)
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
        threads = [
            AirSimTaskThread(self.get_lidar_data(airsim_client, drone_name, client_camera_sensor_data.lidar_list))
        ]
        for i in range(len(threads)):
            threads[i].start()
        
        threads[0].join()


        point_cloud_parameters = threads[0].parameters

        parameters = self.merge(parameters, point_cloud_parameters)

        return parameters

    def get_lidar_data(self, airsim_client:airsim.MultirotorClient, drone_name, lidar_list, parameters = {}):
        parameters['point_cloud'] = {}
        for lidar_face in lidar_list:
            lidar_data = airsim_client.getLidarData(self.lidar_dict[lidar_face], drone_name)
            if "lidar_position" not in parameters.keys():
                parameters['lidar_position'] = {}
            if  "lidar_quaternion" not in parameters.keys():
                parameters['lidar_quaternion'] = {}
            if "point_cloud" not in parameters.keys():
                parameters["point_cloud"] = {}
            if "seg_info" not in parameters.keys():
                parameters["seg_info"] = {}
            
            parameters["lidar_position"][lidar_face] = {
                "x_val" : lidar_data.pose.position.x_val,
                "y_val" : lidar_data.pose.position.y_val,
                "z_val" : lidar_data.pose.position.z_val

            }
            parameters["lidar_quaternion"][lidar_face] = {
            "w_val" : lidar_data.pose.orientation.w_val,
            "x_val" : lidar_data.pose.orientation.x_val,
            "y_val" : lidar_data.pose.orientation.y_val,
            "z_val" : lidar_data.pose.orientation.z_val
            }

            parameters["point_cloud"][lidar_face] = {idx: value for idx, value in enumerate(lidar_data.point_cloud)}

            parameters["seg_info"][lidar_face] = {idx: value for idx, value in enumerate(lidar_data.segmentation)}

        return parameters
        


    def get_lidar_pose(self, lidar_data, parameters = {}):
        pose = lidar_data.pose
        parameters["lidar_position"] = {
            "x_val" : pose.position.x_val,
            "y_val" : pose.position.y_val,
            "z_val" : pose.position.z_val
        }
        parameters["lidar_quaternion"] = {
            "w_val" : pose.orientation.w_val,
            "x_val" : pose.orientation.x_val,
            "y_val" : pose.orientation.y_val,
            "z_val" : pose.orientation.z_val
        }
        
        return parameters
    
    def merge(self, dict1, dict2):
        return {**dict1, **dict2} 