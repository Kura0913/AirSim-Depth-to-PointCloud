from ClientCommand.GetInitialInfo import GetInitialInfo
from ClientCommand.SavePointCloudByDpeth import SavePointCloudByDepth
from ClientCommand.SavePointCloudByLidar import SavePointCloudByLidar
from SocketClient.SocketClient import SocketClient
from ClientObject.ClientCameraSensorData import ClientCameraSensorData
import airsim
import keyboard
import threading


host = ""
port = 40005

client_camera_sensor_data = ClientCameraSensorData()

action_dict = {
    "init" : GetInitialInfo,
    "gen-depth": SavePointCloudByDepth,
    "gen-lidar": SavePointCloudByLidar
}

stop_event = threading.Event()

def init_setting_airsim_client():
    client = airsim.MultirotorClient()
    client.confirmConnection()

    return client

# waiting for pressing 'p' key to stop
def listen_for_stop():    
    keyboard.wait('p')
    stop_event.set()

def input_selection():
    print("========================================")
    print("init: Initial setting for drone and camera.")
    print("gen-depth: Start get point cloud infomation from depth image.")
    print("gen-lidar: Start get point cloud infomation from lidar sensor.")
    print("exit: close client.")

    selection = input("Please select a function to execute:")
    
    return selection

def main():
    airsim_client = init_setting_airsim_client()
    host = input("Please setting the server ip:")
    client = SocketClient(host, port)

    selection = "init"
    # initial setting for drone and camera
    func = action_dict[selection]()
    parameters = func.execute(airsim_client, "", client_camera_sensor_data)
    client.send_command(selection, parameters)
    client.wait_response()
    drone_name = parameters["drone_name"]

    while True:
        selection = input_selection()        
        if selection not in action_dict.keys():
            client.send_command(selection, dict())
            break
        else:
            # set stop loop task
            stop_thread = threading.Thread(target=listen_for_stop)
            stop_thread.start()
            # start the task of getting depth image
            while not stop_event.is_set():
                try:
                    func = action_dict[selection]()
                    parameters = func.execute(airsim_client, drone_name, client_camera_sensor_data)
                except Exception as e:
                    print(e)
                if parameters:
                    client.send_command(selection, parameters)
                    recv_message = client.wait_response()


if __name__ == "__main__":
    main()