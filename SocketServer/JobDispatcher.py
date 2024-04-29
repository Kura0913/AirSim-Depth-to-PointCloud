from ServerCommand.Depth2PointCloud import Depth2PointCloud

class JobDisPatcher:
    def __init__(self):
        self.action = {
            "store_image":Depth2PointCloud()
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command].execute(parameters)

        return execute_result