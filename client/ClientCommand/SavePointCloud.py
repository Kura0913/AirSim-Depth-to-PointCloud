import airsim

class SavePointCloud:
    def __init__(self):
        self.camera_dict = {
            0:"front_camera",
            1:"back_camera",
            2:"right_camera",
            3:"left_camera",
            4:"up_camera",
            5:"down_camera"
        }

    def execute(self, airsim_client:airsim.MultirotorClient, drone_name, camera_list):
        '''
        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        ----------------------------------------------
        Return:{
            drone_name : (Char)
            drone_position : [x_val, y_val, z_val] (NED)
            drone_quaternion : [w_val, x_val, y_val, z_val]
            depth_image : {camera_face : image_array(float)}
            rgb_image : {camera_face : image_array(uint8)}
        }        
        '''
        parameters = {
            "drone_name":drone_name
        }

        parameters = self.get_drone_pose(airsim_client, drone_name, parameters)
        parameters = self.get_depth_image(airsim_client, drone_name, camera_list, parameters)
    
    def get_drone_pose(self, airsim_client:airsim.MultirotorClient, drone_name, parameters):
        pose = airsim_client.simGetVehiclePose(drone_name)
        parameters["drone_position"] = [pose.position.x_val, pose.position.y_val, pose.position.z_val]
        parameters["drone_quaternion"] = [pose.orientation.w_val, pose.orientation.x_val, pose.orientation.y_val, pose.orientation.z_val]

        return parameters
    
    def get_depth_image(self, airsim_client:airsim.MultirotorClient, drone_name, camera_list, parameters):
        depth_image_request_list = []
        for camera_face in camera_list:
            depth_image_request_list = depth_image_request_list + [airsim.ImageRequest(self.camera_dict[camera_face], airsim.ImageType.DepthPerspective, True)]
        images = airsim_client.simGetImages(depth_image_request_list, drone_name)

        for idx, image in enumerate(images):
            if not parameters["depth_image"]:
                parameters["depth_image"] = {}
            parameters["depth_image"][camera_list[idx]] = image.image_data_float
        
        return parameters
    
    def get_scene_image(self, airsim_client:airsim.MultirotorClient, drone_name, camera_list, parameters):
        depth_image_request_list = []
        for camera_face in camera_list:
            depth_image_request_list = depth_image_request_list + [airsim.ImageRequest(self.camera_dict[camera_face], airsim.ImageType.Scene)]
        images = airsim_client.simGetImages(depth_image_request_list, drone_name)

        for idx, image in enumerate(images):
            if not parameters["rgb_image"]:
                parameters["rgb_image"] = {}
            parameters["rgb_image"][camera_list[idx]] = image.image_data_uint8
        
        return parameters