from ServerCommand.StoreImage import StoreImage

class JobDisPatcher:
    def __init__(self):
        self.action = {
            "store":StoreImage
        }

    def job_execute(self, command, parameters):
        execute_result = self.action[command]().execute(parameters)

        return execute_result