from ClientCommand.GetCameraInfo import GetCameraInfo
from ClientCommand.SavePointCloud import SavePointCloud
from SocketClient.SocketClient import SocketClient
import airsim
import numpy as np

host = ""
port = 40005

action_dict = {
    "init" : GetCameraInfo,
    "start": SavePointCloud
}

def init_setting_airsim_client():
    client = airsim.MultirotorClient()
    client.confirmConnection()

    return client

def input_selection():
    print("========================================")
    print("init: Initial setting for drone and camera.")
    print("start: Start get point cloud infomation.")
    print("exit: close client.")

    selection = input("Please select a function to execute:")
    
    return selection

def main():
    airsim_client = init_setting_airsim_client()
    client = SocketClient(host, port)

    selection = "init"    
    # initial setting for drone and camera
    func = action_dict[selection]()
    parameters = func.execute(airsim_client)
    client.send_command(selection, parameters)
    drone_name = parameters["drone_name"]
    camera_list = []

    for camera_face, _ in parameters["camera"]:
        camera_list.append(camera_face)
    result = client.wait_response()

    while True:
        selection = input_selection()
        if selection not in action_dict.keys():
            client.send_command(selection, dict())
            break
        else:
            try:
                func = action_dict[selection]()
                parameters = func.execute(airsim_client, drone_name, camera_list)
            except Exception as e:
                print(e)
            if parameters:
                client.send_command(selection, parameters)
                result = client.wait_response()
