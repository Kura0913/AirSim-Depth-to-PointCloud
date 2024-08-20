import airsim
from ClientObject.ClientCameraSensorData import ClientCameraSensorData
import numpy as np
from scipy.spatial.transform import Rotation
import os
import json
import time 

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
            "front_lidar":0,
            "back_lidar": 1,
            "right_lidar": 2,
            "left_lidar": 3
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
        start_time = time.time()
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
        parameters = self.get_camera_info(airsim_client, drone_name, parameters, data, client_camera_sensor_data)
        parameters = self.get_lidar_info(parameters, data, client_camera_sensor_data)
        
        end_time = time.time()
        print(f"execute time: {end_time - start_time:.4f} seconds.")
        return parameters
        
    def get_camera_info(self, airsim_client:airsim.MultirotorClient, drone_name, parameters, data, client_camera_sensor_data:ClientCameraSensorData):
        parameters["camera"] = {}

        if data:
            cameras = data['Vehicles']['drone_1']['Cameras']
            for camera_name in cameras.keys():
                camera_info = airsim_client.simGetCameraInfo(camera_name, drone_name)
                camera_face = self.camera_dict[camera_name]
                if "fov" not in parameters.keys():
                    parameters["fov"] = camera_info.fov
                if camera_face not in parameters["camera"].keys():
                    parameters["camera"][camera_face] = {}
                if camera_face not in parameters["camera"].keys():
                    parameters["camera"][camera_face] = {}

                parameters["camera"][camera_face]["translation_x"] = cameras = data['Vehicles']['drone_1']['Cameras'][camera_name]["X"]
                parameters["camera"][camera_face]["translation_y"] = cameras = data['Vehicles']['drone_1']['Cameras'][camera_name]["Y"]
                parameters["camera"][camera_face]["translation_z"] = cameras = data['Vehicles']['drone_1']['Cameras'][camera_name]["Z"]
                # camera_quaternion = [x_val, y_val, z_val, w_val]
                camera_quaternion = self.euler_to_quaternion(data['Vehicles']['drone_1']['Cameras'][camera_name]["Roll"], data['Vehicles']['drone_1']['Cameras'][camera_name]["Pitch"], data['Vehicles']['drone_1']['Cameras'][camera_name]["Yaw"])
                parameters["camera"][camera_face]["quaternion_w"] = camera_quaternion[3]
                parameters["camera"][camera_face]["quaternion_x"] = camera_quaternion[0]
                parameters["camera"][camera_face]["quaternion_y"] = camera_quaternion[1]
                parameters["camera"][camera_face]["quaternion_z"] = camera_quaternion[2]
                client_camera_sensor_data.camera_list.append(camera_face)
                print(f"Get camera: {camera_name} info success!!")

        return parameters
    
    def get_lidar_info(self, parameters, data, client_camera_sensor_data:ClientCameraSensorData):
        parameters["lidar"] = {}
        if data:
            lidar_sensors = data['Vehicles']['drone_1']['Sensors']
            for lidar_name in lidar_sensors.keys():
                lidar_face = self.lidar_dict[lidar_name]
                if "lidar" not in parameters.keys():
                    parameters['lidar'] = {}
                if lidar_face not in parameters['lidar'].keys():
                    parameters['lidar'][lidar_face] = {}
                parameters['lidar'][lidar_face]['translation_x'] = data['Vehicles']['drone_1']['Sensors'][lidar_name]["X"]
                parameters['lidar'][lidar_face]["translation_y"] = data['Vehicles']['drone_1']['Sensors'][lidar_name]["Y"]
                parameters['lidar'][lidar_face]["translation_z"] = data['Vehicles']['drone_1']['Sensors'][lidar_name]["Z"]
                # lidar_quaternion = [x_val, y_val, z_val, w_val]
                lidar_quaternion = self.euler_to_quaternion(data['Vehicles']['drone_1']['Sensors'][lidar_name]["Roll"], data['Vehicles']['drone_1']['Sensors'][lidar_name]["Pitch"], data['Vehicles']['drone_1']['Sensors'][lidar_name]["Yaw"])
                parameters['lidar'][lidar_face]["quaternion_w"] = lidar_quaternion[3]
                parameters['lidar'][lidar_face]["quaternion_x"] = lidar_quaternion[0]
                parameters['lidar'][lidar_face]["quaternion_y"] = lidar_quaternion[1]
                parameters['lidar'][lidar_face]["quaternion_z"] = lidar_quaternion[2]

                client_camera_sensor_data.lidar_list.append(lidar_face)
                print(f"Get lidar: {lidar_name} info success!!")

        return parameters

    def get_image_size(self, parameters, json_data, vehicle_name):
        camera_data = json_data['Vehicles'][vehicle_name]['Cameras']['front_camera']["CaptureSettings"][0]
        parameters["width"] = int(camera_data["Width"])
        parameters["height"] = int(camera_data["Height"])
        
        return parameters

    def euler_to_quaternion(self, roll, pitch, yaw):
        '''
        return: [x_val, y_val, z_val, w_val]
        '''
        roll_rad = np.radians(roll)
        pitch_rad = np.radians(pitch)
        yaw_rad = np.radians(yaw)
        quaternion = Rotation.from_euler('xyz', [roll_rad, pitch_rad, yaw_rad], degrees=False).as_quat()

        return quaternion