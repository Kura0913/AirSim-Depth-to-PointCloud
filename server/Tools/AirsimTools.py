import numpy as np
from scipy.spatial.transform import Rotation

class AirsimTools:
    def __init__(self):
        pass

    # check the value wheather equals to "negative zero",if yes, set them to 0.0
    def negative_zero_to_zero(self, x, y, z):
        '''
        Trans negative 0 to 0
        '''
        if x == -0.0:
            x = float('0.0')
        if y == -0.0:
            y = float('0.0')
        if z == -0.0:
            z = float('0.0')

        return [x, y, z]
    
    def quaternion2ratate(self, quaternion):
        '''
        quaternion: vehicle pose's quaternion
        position: vehicle pose's position
        '''
        return Rotation.from_quat(quaternion).as_matrix()
    

    def relative2absolute(self, target_positions, vehicle_position, vehicle_quaternion):
        '''
         Args:
            target_positions (np.ndarray):  shape(3, u, v), u:image height, v: image width
            vehicle_position (np.ndarray): vehicle pose's position
            vehicle_quaternion (np.ndarray): vehicle pose's quaternion

        ---------------------------------------------------------
        Return : 
            absolute_positions (np.ndarray): Absolute position point cloud information, the shape is (u * v, 3), each row represents an absolute position point, and each column represents the x, y, z coordinates respectively
        '''
        target_positions = target_positions.reshape(3, -1) # convert the shape from (3, u, v) to (3, u*v)
        relative_positions_without_rotate = np.dot(Rotation.from_quat(vehicle_quaternion).as_matrix(), target_positions)
        absolute_positions = (relative_positions_without_rotate.T + vehicle_position).T
        absolute_positions = absolute_positions.T.reshape(-1, 3) # convert the shape to (u*v, 3)
        return absolute_positions
    
    def ned2cartesian(self, n_val, e_val, d_val):
        ned = self.negative_zero_to_zero(n_val, e_val, d_val)
        return [ned[1], ned[0], -ned[2]]
    