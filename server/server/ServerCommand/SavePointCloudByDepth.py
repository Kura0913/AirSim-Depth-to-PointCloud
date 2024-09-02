import time
from datetime import datetime
import json

MIN_DEPTH_METERS = 0
MAX_DEPTH_METERS = 100
LIMIT_DEPTH = 50

class SavePointCloudByDepth:
    def __init__(self):
        self.file_path = "./json_file/depth/"

    def execute(self, parameters):
        '''
        parameters : {
            'drone_name' : (Char)
            'drone_position' : {'x_val', 'y_val', 'z_val'} (NED)
            'drone_quaternion' : {'w_val', 'x_val', 'y_val', 'z_val'}
            'depth_image' : {
                'camera_face' : {
                    id : pixel_value
                }
            'rgb_image' : {
                'camera_face' : {
                    id : pixel_value
                }
            }
        }

        camera_face:
        front: 0, back: 1, right: 2, left: 3, up: 4, down: 5
        '''
        start_time = time.time()
        try:
            self.save_json_file(parameters)
            end_time = time.time()
            print(f"execute time: {end_time - start_time:.4f} seconds.")
            return {"status" : "ok", "message" : "save point cloud complete."}
        except Exception as e:
            return{"status" : "fail", "message" : "save point cloud failed, please check the previously sent parameters.", "exception" : str(e)}
    
    def save_json_file(self, parameters):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"data_{timestamp}.json"
        with open(self.file_path + filename, 'w', encoding='utf-8') as json_file:
            json.dump(parameters, json_file, ensure_ascii=False, indent=4)