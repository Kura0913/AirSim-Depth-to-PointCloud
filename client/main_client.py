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
    0: GetInitialInfo,
    1: "clear DB data",
    2: SavePointCloudByDepth,
    3: SavePointCloudByLidar
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
    print("0: Initial setting for drone, camera and lidar.")
    print("1: Clear data in DB.")
    print("2: Start get point cloud infomation from depth image.")
    print("3: Start get point cloud infomation from lidar sensor.")
    print("others: close client.")

    try:
        selection = int(input("Please select a function to execute:"))
    except:
        return -1
    
    return selection

def main():
    airsim_client = init_setting_airsim_client()
    host = input("Please setting the server ip:")
    client = SocketClient(host, port)

    selection = 0
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
        elif selection == 0:
            func = action_dict[selection]()
            parameters = func.execute(airsim_client, drone_name, client_camera_sensor_data)
            client.send_command(selection, parameters)
            client.wait_response()
        elif selection == 1:
            client.send_command(selection, {"message": "clear DB"})
            client.wait_response()
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