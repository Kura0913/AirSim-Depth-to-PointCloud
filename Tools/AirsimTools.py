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
    
    def quaternion2ratate(quaternion, position):
        '''
        quaternion: vehicle pose's quaternion
        position: vehicle pose's position
        '''
        return np.dot(Rotation.from_quat(quaternion).as_matrix(), position)
    

    def relative2absolute(target_position, body_position, body_quaternion):
        '''
        target_position: the point get from sensor is relative position
        body_position: vehicle pose's position
        body_quaternion: vehicle pose's quaternion
        '''
        rotated_position = np.dot(Rotation.from_quat(body_quaternion).as_matrix(), target_position)

        return body_position + rotated_position