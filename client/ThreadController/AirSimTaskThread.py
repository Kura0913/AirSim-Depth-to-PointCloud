import threading

class AirSimTaskThread(threading.Thread):
        def __init__(self, task):
            threading.Thread.__init__(self)
            self.parameters = {}
            self.task = task
        def run(self):
            self.parameters = self.task