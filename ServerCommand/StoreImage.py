import math
import numpy as np
from Tools.AirsimTools import AirsimTools
from scipy.spatial.transform import Rotation as R
from DBController.PointCloudInfoTable import PointCloudInfoTable

class StoreImage:
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
        parameters :{
            drone_position : [x_val, y_val, z_val] (NED)
            drone_quaternion : [w_val, x_val, y_val, z_val]
            depth_image : numpy.array()
            rgb_image : numpy.array()
        }
        '''
        point_cloud_list = []

        ### Intrinsic parameters matrix
        K = np.array([
            [self.fx, 0, self.cx, 0],
            [0, self.fy, self.cy, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        ### Extrinsic Parameters
        # translation matrix
        t = np.array([0, 0, 0]) # input
        # rotate matrix
        R = np.array([          # input
            [1, 0, 0, t[0]],
            [0, 1, 0, t[1]],
            [0, 0, 1, t[2]],
            [0, 0, 0, 1]
        ])        
        
        for u in range(self.width):
            for v in range(self.height):
                z = parameters['depth_image'][u, v]/1000 # divide by 1000 to convert z to meters
                # limit the range in 0 to 30 of saved point cloud
                if z == 0 or z > 30:
                    continue
                
                pixel_matrix = np.array([u, v, 1, 1/z]).T # set pixel matrix

                camera_matrix = K.dot(R)
                camera_matrix_inv = np.linalg.inv(camera_matrix) # get inverse camera matrix
                point_cloud_matrix = z * camera_matrix_inv.dot(pixel_matrix)
                point_cloud_info = [point_cloud_matrix[0], point_cloud_matrix[1], point_cloud_matrix[2]] # relative position
                # convert relative position to abs position
                drone_position = AirsimTools.ned2cartesian(parameters['drone_position'][0], parameters['drone_position'][1], parameters['drone_position'][2]) # cartesian coordinate system
                drone_quaternion = [parameters['drone_quaternion'][0], parameters['drone_quaternion'][1], parameters['drone_quaternion'][2], parameters['drone_quaternion'][3]]
                point_cloud_info = AirsimTools.relative2absolute(point_cloud_info, drone_position, drone_quaternion)

                point_cloud_list.append(point_cloud_info)

        PointCloudInfoTable.insert_point_clouds(point_cloud_list)
        return
    
