import numpy as np
from scipy.spatial.transform import Rotation

class AirsimTools:
    def __init__(self):
        pass

    # check the value wheather equals to "negative zero",if yes, set them to 0.0
    def negative_zero_to_zero(x, y, z):
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
    
    def quaternion2ratate(quaternion):
        '''
        quaternion: vehicle pose's quaternion
        position: vehicle pose's position
        '''
        return Rotation.from_quat(quaternion).as_matrix()
    

    def relative2absolute(target_position, vehicle_position, vehicle_quaternion):
        '''
        target_position: [x_val, y_val, z_val]the point get from sensor is relative position
        body_position: [x_val, y_val, z_val]vehicle pose's position
        body_quaternion: [w_val, x_val, y_val, z_val]vehicle pose's quaternion
        '''
        relative_position_without_rotate = np.dot(Rotation.from_quat(vehicle_quaternion).as_matrix(), target_position)

        return vehicle_position + relative_position_without_rotate
    
    def ned2cartesian(n_val, e_val, d_val):
        return [e_val, n_val, -d_val]
    