import math

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
            depth_image : numpy.array()
            rgb_image : numpy.array()
        }
        '''
        
        


        

        return
    
