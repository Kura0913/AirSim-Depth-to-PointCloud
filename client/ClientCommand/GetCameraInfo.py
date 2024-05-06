import airsim

class GetCameraInfo:
    def __init__(self):
        self.camera_dict = {
            "front_camera":0,
            "back_camera":1,
            "right_camera":2,
            "left_camera":3,
            "up_camera":4,
            "down_camera":5
        }

    def execute(self, airsim_client:airsim.MultirotorClient, drone_name = "", camera_list = []):
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
            }
        }
        '''
        
        drone_name = input("Please input drone's name:")
        parameters = {"drone_name" : drone_name}
        parameters = self.get_image_size(parameters)
        parameters = self.get_camera_info(airsim_client, drone_name, parameters)
        
    def get_camera_info(self, airsim_client:airsim.MultirotorClient, drone_name, parameters):
        parameters["camera"] = {}
        try:
            for camera_name, camera_face in self.camera_dict.items():
                pose = airsim_client.simGetCameraInfo(camera_name, drone_name).pose
                if not parameters["fov"]:
                    parameters["fov"] = airsim_client.simGetCameraInfo(camera_name, drone_name).fov
                if not parameters["camera"]:
                    parameters["camera"] = {}
                if not parameters["camera"][camera_face]:
                    parameters["camera"][camera_face] = {}
                parameters["camera"][camera_face]["translation_x"] = pose.position.x_val
                parameters["camera"][camera_face]["translation_y"] = pose.position.y_val
                parameters["camera"][camera_face]["translation_z"] = pose.position.z_val
                parameters["camera"][camera_face]["quaternion_w"] = pose.orientation.w_val
                parameters["camera"][camera_face]["quaternion_x"] = pose.orientation.x_val
                parameters["camera"][camera_face]["quaternion_y"] = pose.orientation.y_val
                parameters["camera"][camera_face]["quaternion_z"] = pose.orientation.z_val
        except:
            print(f"The camera:{camera_name} is not exist.")


        return parameters
    
    def get_image_size(self, parameters):
        while True:
            try:
                width = int(input("Please input the image width(integer):"))
                parameters["width"] = width
                break
            except:
                print("Please input with integer, try again.")
        while True:
            try:
                height = int(input("Please input the image height(integer):"))
                parameters["height"] = height
                break
            except:
                print("Please input with integer, try again.")
        
        return parameters
