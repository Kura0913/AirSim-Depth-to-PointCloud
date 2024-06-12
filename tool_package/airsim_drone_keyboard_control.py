import airsim
import numpy as np
import keyboard

# 連接到AirSim
client = airsim.MultirotorClient()
client.confirmConnection()

# 允許API控制無人機
client.enableApiControl(True)
client.armDisarm(True)

# 獲取初始位置和旋轉信息
initial_pose = client.simGetVehiclePose()
initial_position = initial_pose.position
initial_rotation = initial_pose.orientation

# 設置移動速度和旋轉速度
move_speed = 10.0  # 調整為適當的移動速度
during_time = 0.1
rotate_speed = 100.0  # 調整為適當的旋轉速度

while True:
    # 獲取當前位置和旋轉信息
    current_pose = client.simGetVehiclePose()
    current_position = current_pose.position
    current_rotation = current_pose.orientation
    # print(f'drone_position:{current_position}')
    # print(f'current_rotation:{current_rotation}')
    # 監聽鍵盤输入
    if keyboard.is_pressed('w'):
        client.moveByVelocityBodyFrameAsync(move_speed, 0, 0, during_time).join()
    elif keyboard.is_pressed('s'):
        client.moveByVelocityBodyFrameAsync(-move_speed, 0, 0, during_time).join()
    elif keyboard.is_pressed('a'):
        client.moveByVelocityBodyFrameAsync(0, -move_speed, 0, during_time).join()
    elif keyboard.is_pressed('d'):
        client.moveByVelocityBodyFrameAsync(0, move_speed, 0, during_time).join()
    elif keyboard.is_pressed('left_shift'):
        client.moveByVelocityBodyFrameAsync(0, 0, move_speed, during_time).join()
    elif keyboard.is_pressed('space'):
        client.moveByVelocityBodyFrameAsync(0, 0, -move_speed, during_time).join()
    elif keyboard.is_pressed('q'):
        client.rotateByYawRateAsync(-rotate_speed, during_time).join()
    elif keyboard.is_pressed('e'):
        client.rotateByYawRateAsync(rotate_speed, during_time).join()
    elif keyboard.is_pressed('x'):
        lidarData = client.getLidarData('front_lidar')
        print(lidarData)
    else:
        client.moveByVelocityBodyFrameAsync(0, 0, 0, during_time).join()
        client.rotateByYawRateAsync(0, during_time).join()
    # 休眠一小段時間，避免過於頻繁的操作
    airsim.time.sleep(0.01)