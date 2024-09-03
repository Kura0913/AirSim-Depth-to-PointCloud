from DBController.CameraInfoTable import CameraInfoTable
from DBController.LidarInfoTable import LidarInfoTable
from DBController.DroneInfoTable import DroneInfoTable

class DBClearer:
    def __init__(self) -> None:
        pass

    def execute(self, parameters):
        CameraInfoTable().delete_all_camera()
        LidarInfoTable().delete_all_lidar()
        DroneInfoTable().delete_all_drone()

        return {"status" : "ok", "message" : "Clear completed."}