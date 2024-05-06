from ServerCommand.GetCameraInfo import GetCameraInfo
from ServerCommand.SavePointCloud import SavePointCloud

class JobDisPatcher:
    def __init__(self):
        self.action = {
            "init":GetCameraInfo,
            "save":SavePointCloud
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command]().execute(parameters)

        return execute_result