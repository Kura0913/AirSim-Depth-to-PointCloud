from ServerCommand.GetInitalInfo import GetInitialInfo
from ServerCommand.SavePointCloudByDepth import SavePointCloudByDepth

class JobDisPatcher:
    def __init__(self):
        self.action = {
            "init":GetInitialInfo,
            "gen-depth":SavePointCloudByDepth
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command]().execute(parameters)

        return execute_result