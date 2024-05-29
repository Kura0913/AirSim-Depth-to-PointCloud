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
    

    def relative2absolute_quaternion(self, target_positions, reference_object_position, reference_object_quaternion, reshape:bool = True):
        '''
         Args:
            target_positions (np.ndarray):  shape(3, u, v), u:image height, v: image width
            reference_object_position (np.ndarray)
            reference_object_quaternion (np.ndarray)

        ---------------------------------------------------------
        Return :
            reshape True: absolute_positions (np.ndarray): Point cloud information, the shape is (u * v, 3)
            reshape False: absolute_positions (np.ndarray): Point cloud information, the shape is (3, u, v)
        '''
        u, v = target_positions.shape[1], target_positions.shape[2]
        target_positions = target_positions.reshape(3, -1) # convert the shape from (3, u, v) to (3, u*v)
        relative_positions_without_rotate = np.dot(target_positions.T, Rotation.from_quat(reference_object_quaternion).as_matrix())
        absolute_positions = (relative_positions_without_rotate + reference_object_position).T
        if reshape:                        
            absolute_positions = absolute_positions.T.reshape(-1, 3) # convert the shape to (u*v, 3)
        else:
            absolute_positions = absolute_positions.reshape(3, u, v) # convert the shape to (3, u, v)
        return absolute_positions
    
    def relative2absolute_rotate(self, target_positions, reference_object_position, reference_object_rotate, reshape:bool = True):
        '''
         Args:
            target_positions (np.ndarray):  shape(3, u, v), u:image height, v: image width
            reference_object_position (np.ndarray)
            reference_object_quaternion (np.ndarray)

        ---------------------------------------------------------
        Return :
            reshape True: absolute_positions (np.ndarray): Point cloud information, the shape is (u * v, 3)
            reshape False: absolute_positions (np.ndarray): Point cloud information, the shape is (3, u, v)
        '''
        u, v = target_positions.shape[1], target_positions.shape[2]
        target_positions = target_positions.reshape(3, -1) # convert the shape from (3, u, v) to (3, u*v)
        relative_positions_without_rotate = np.dot(target_positions.T, reference_object_rotate)
        absolute_positions = (relative_positions_without_rotate + reference_object_position).T
        if reshape:
            absolute_positions = absolute_positions.T.reshape(-1, 3) # convert the shape to (u*v, 3)
        else:
            absolute_positions = absolute_positions.reshape(3, u, v) # convert the shape to (3, u, v)
        return absolute_positions
    
    def ned2cartesian(self, n_val, e_val, d_val):
        ned = self.negative_zero_to_zero(n_val, e_val, d_val)
        return [ned[1], -ned[2], -ned[0]]
    
    def depth_conversion(self, point_depth, f_x):
        H = point_depth.shape[0]
        W = point_depth.shape[1]
        i_c = np.float(H) / 2 - 1
        j_c = np.float(W) / 2 - 1
        columns, rows = np.meshgrid(np.linspace(0, W-1, num=W), np.linspace(0, H-1, num=H))
        distance_from_center = ((rows - i_c)**2 + (columns - j_c)**2)**(0.5)
        plane_depth = point_depth / (1 + (distance_from_center / f_x)**2)**(0.5)
        return plane_depth