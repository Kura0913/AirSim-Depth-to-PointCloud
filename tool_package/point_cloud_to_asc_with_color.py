import sqlite3

def export_to_asc(db_path, output_path):
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询点云数据
    cursor.execute("SELECT point_x, point_y, point_z, color_r, color_g, color_b FROM point_cloud_info")
    rows = cursor.fetchall()
    
    # 打开ASC文件以写入
    with open(output_path, 'w') as file:
        # 写入点云数据
        for row in rows:
            point_x, point_y, point_z, color_r, color_g, color_b = row
            # 将数据写成ASC格式（通常是空间坐标和颜色值）
            file.write(f"{point_x} {point_y} {point_z} {color_r} {color_g} {color_b}\n")
    
    # 关闭数据库连接
    conn.close()

# 示例使用
db_path = 'D:\\Colosseum\\Colosseum5_2\\PythonClient\\detection_1\\AirSim-Depth-to-PointCloud\\server\\point_cloud.db'  # 替换为你的数据库路径
output_path = 'cloud_point_with_color.asc'    # 替换为你想要输出的ASC文件路径
export_to_asc(db_path, output_path)
print(f"Data has been exported to {output_path}")
