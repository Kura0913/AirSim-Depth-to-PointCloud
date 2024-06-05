from ClientCommand.GetCameraInfo import GetCameraInfo
from ClientCommand.SavePointCloudByDpeth import SavePointCloudByDepth
from SocketClient.SocketClient import SocketClient
import airsim
import keyboard
import threading

host = ""
port = 40005

action_dict = {
    "init" : GetCameraInfo,
    "gen-depth": SavePointCloudByDepth
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
# loop to get depth image, stop loop when stop event is set.
def task(selection, client, airsim_client, drone_name, camera_list):
    while not stop_event.is_set():
                try:
                    func = action_dict[selection]()
                    parameters = func.execute(airsim_client, drone_name, camera_list)
                except Exception as e:
                    print(e)
                if parameters:
                    client.send_command(selection, parameters)
                    recv_message = client.wait_response()

def input_selection():
    print("========================================")
    print("init: Initial setting for drone and camera.")
    print("gen-depth: Start get point cloud infomation from depth image.")
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
    parameters = func.execute(airsim_client)
    client.send_command(selection, parameters)
    client.wait_response()
    drone_name = parameters["drone_name"]
    camera_list = []

    for camera_face, _ in parameters["camera"].items():
        camera_list.append(camera_face)

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
                    parameters = func.execute(airsim_client, drone_name, camera_list)
                except Exception as e:
                    print(e)
                if parameters:
                    client.send_command(selection, parameters)
                    recv_message = client.wait_response()

            # task(selection, client, airsim_client, drone_name, camera_list)

if __name__ == "__main__":
    main()