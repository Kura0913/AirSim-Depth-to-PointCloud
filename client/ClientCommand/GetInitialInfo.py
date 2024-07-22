import airsim
from ClientObject.ClientCameraSensorData import ClientCameraSensorData
import os
import json

class GetInitialInfo:
    def __init__(self):
        self.camera_dict = {
            "front_camera":0,
            # "back_camera":1,
            # "right_camera":2,
            # "left_camera":3,
            # "up_camera":4,
            # "down_camera":5
        }

        self.lidar_dict = {
            "front_lidar":0
        }

    def execute(self, airsim_client:airsim.MultirotorClient, drone_name:str, client_camera_sensor_data:ClientCameraSensorData):
        '''
        Return : {
            drone_name,
            fov,
            width,
            height,
            camera:{
                camera_face : {
                    translation_x:float,
                    translation_y:float,
                    translation_z:float,
                    quaternion_w:float,
                    quaternion_x:float,
                    quaternion_y:float,
                    quaternion_z:float
                }
            },
            lidar:{
                lidar_face:{
                    translation_x:float,
                    translation_y:float,
                    translation_z:float,
                    quaternion_w:float,
                    quaternion_x:float,
                    quaternion_y:float,
                    quaternion_z:float
                }
            }
        }
        '''
        user_home = os.path.expanduser('~')
        settings_path = os.path.join(user_home, 'Documents', 'AirSim', 'settings.json')
        with open(settings_path, 'r') as file:
            data = json.load(file)
        if data:
            vehicle_names = []
            vehicles = data.get('Vehicles', {})
            for vehicle, _ in vehicles.items():
                vehicle_names.append(vehicle)

        drone_name = vehicle_names[0]
        parameters = {"drone_name" : vehicle_names[0]}
        parameters = self.get_image_size(parameters, data, drone_name)
        parameters = self.get_camera_info(airsim_client, drone_name, parameters, client_camera_sensor_data)
        parameters = self.get_lidar_info(airsim_client, drone_name, parameters, client_camera_sensor_data)

        return parameters
        
    def get_camera_info(self, airsim_client:airsim.MultirotorClient, drone_name, parameters, client_camera_sensor_data:ClientCameraSensorData):
        parameters["camera"] = {}        
        for camera_name, camera_face in self.camera_dict.items():
            try:
                pose = airsim_client.simGetCameraInfo(camera_name, drone_name).pose
                if "fov" not in parameters.keys():
                    parameters["fov"] = airsim_client.simGetCameraInfo(camera_name, drone_name).fov
                if "camera" not in parameters.keys():
                    parameters["camera"] = {}
                if camera_face not in parameters["camera"].keys():
                    parameters["camera"][camera_face] = {}
                parameters["camera"][camera_face]["translation_x"] = pose.position.x_val
                parameters["camera"][camera_face]["translation_y"] = pose.position.y_val
                parameters["camera"][camera_face]["translation_z"] = pose.position.z_val
                parameters["camera"][camera_face]["quaternion_w"] = pose.orientation.w_val
                parameters["camera"][camera_face]["quaternion_x"] = pose.orientation.x_val
                parameters["camera"][camera_face]["quaternion_y"] = pose.orientation.y_val
                parameters["camera"][camera_face]["quaternion_z"] = pose.orientation.z_val
                client_camera_sensor_data.camera_list.append(camera_face)
                print(f"Get camera:{camera_name} info success!!")
            except:
                print(f"The camera:{camera_name} is not exist.")

        return parameters
    
    def get_lidar_info(self, airsim_client:airsim.MultirotorClient, drone_name, parameters, client_camera_sensor_data:ClientCameraSensorData):
        parameters["lidar"] = {}        
        for lidar_name, lidar_face in self.lidar_dict.items():
            try:
                pose = airsim_client.getLidarData(lidar_name, drone_name).pose
                if "lidar" not in parameters.keys():
                    parameters['lidar'] = {}
                if lidar_face not in parameters['lidar'].keys():
                    parameters['lidar'][lidar_face] = {}
                parameters['lidar'][lidar_face]['translation_x'] =pose.position.x_val
                parameters['lidar'][lidar_face]["translation_y"] = pose.position.y_val
                parameters['lidar'][lidar_face]["translation_z"] = pose.position.z_val
                parameters['lidar'][lidar_face]["quaternion_w"] = pose.orientation.w_val
                parameters['lidar'][lidar_face]["quaternion_x"] = pose.orientation.x_val
                parameters['lidar'][lidar_face]["quaternion_y"] = pose.orientation.y_val
                parameters['lidar'][lidar_face]["quaternion_z"] = pose.orientation.z_val
                client_camera_sensor_data.lidar_list.append(lidar_face)
                print(f"Get lidar{lidar_name} info success!!")
            except:
                print(f"The lidar:{lidar_name} is not exist.")
        return parameters

    def get_image_size(self, parameters, json_data, vehicle_name):
        camera_data = json_data['Vehicles'][vehicle_name]['Cameras']['front_camera']["CaptureSettings"][0]
        parameters["width"] = int(camera_data["Width"])
        parameters["height"] = int(camera_data["Height"])

        # while True:
        #     try:
        #         width = int(input("Please input the image width(integer):"))
        #         parameters["width"] = width
        #         break
        #     except:
        #         print("Please input with integer, try again.")
        # while True:
        #     try:
        #         height = int(input("Please input the image height(integer):"))
        #         parameters["height"] = height
        #         break
        #     except:
        #         print("Please input with integer, try again.")
        
        return parameters
