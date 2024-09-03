from ServerCommand.GetInitalInfo import GetInitialInfo
from ServerCommand.SavePointCloudByDepth import SavePointCloudByDepth
from ServerCommand.SavePointCloudByLidar import SavePointCloudByLidar
from ServerCommand.DBClearer import DBClearer

class JobDisPatcher:
    def __init__(self):
        self.action = {
            0:GetInitialInfo,
            1:DBClearer,
            2:SavePointCloudByDepth,
            3:SavePointCloudByLidar
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command]().execute(parameters)

        return execute_result