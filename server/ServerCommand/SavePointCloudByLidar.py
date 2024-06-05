import math
import numpy as np
import airsim
from Tools.AirsimTools import AirsimTools
from DBController.PointCloudInfoTable import PointCloudInfoTable
from DBController.DroneInfoTable import DroneInfoTable
from DBController.CameraInfoTable import CameraInfoTable
from scipy.spatial.transform import Rotation

class SavePointCloudByLidar:
    def __init__(self):
        pass
    def execute(self, parameters):
        """
        parameters : {
            'drone_name' : (Char)
            'drone_position' : {'x_val', 'y_val', 'z_val'} (NED)
            'drone_quaternion' : {'w_val', 'x_val', 'y_val', 'z_val'}
            'point_cloud' : {
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
        """