import sqlite3


def interpolate_color(value, min_val, max_val, color1, color2):
    ratio = (value - min_val) / (max_val - min_val)
    r = int(color1[0] + ratio * (color2[0] - color1[0]))
    g = int(color1[1] + ratio * (color2[1] - color1[1]))
    b = int(color1[2] + ratio * (color2[2] - color1[2]))
    return (r, g, b)

def get_color(norm_y):
    if norm_y < 0.2:  # 蓝 -> 绿
        color = interpolate_color(norm_y, 0.0, 0.2, (0, 0, 255), (0, 255, 0))
    elif norm_y < 0.4:  # 绿 -> 黄
        color = interpolate_color(norm_y, 0.2, 0.4, (0, 255, 0), (255, 255, 0))
    elif norm_y < 0.6:  # 黄 -> 红
        color = interpolate_color(norm_y, 0.4, 0.6, (255, 255, 0), (255, 0, 0))
    elif norm_y < 0.8:  # 红 -> 紫
        color = interpolate_color(norm_y, 0.6, 0.8, (255, 0, 0), (128, 0, 128))
    else:  # 紫 -> 白
        color = interpolate_color(norm_y, 0.8, 1.0, (128, 0, 128), (255, 255, 255))
    return color

def main():
    # connect to your database
    connection = sqlite3.connect('D:\\Colosseum\\Colosseum5_2\\PythonClient\\detection_1\\AirSim-Depth-to-PointCloud\\server\\point_cloud.db')  # your db file
    cursor = connection.cursor()

    # fetch all point cloud in database
    cursor.execute("SELECT point_x, point_y, point_z FROM point_cloud_info")
    points = cursor.fetchall()
    # get point_y's min and max
    cursor.execute("SELECT MIN(point_y), MAX(point_y) FROM point_cloud_info")
    min_y, max_y = cursor.fetchone()

    # close the connection
    connection.close()

    # 写入ASC文件
    with open('point_cloud.asc', 'w') as file:
        for point in points:
            if max_y != min_y:
                nom_y = (point[1] - min_y) / (max_y - min_y)  # nomalize point_y
            else:
                nom_y = 0.5
            # set color
            color = get_color(nom_y)

            line = f"{point[0]} {point[1]} {point[2]} {color[0]} {color[1]} {color[2]}\n"
            file.write(line)

    print("ASC file with color information has been created successfully.")

main()