from ServerCommand.StoreImage import StorePointCloud

class JobDisPatcher:
    def __init__(self):
        self.action = {
            "store":StorePointCloud
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command]().execute(parameters)

        return execute_result