import pymongo
import numpy as np

# 設定 MongoDB 連接
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["aiotlab"]
collection = db["point_cloud_info"]

# 查詢所有點雲資料
cursor = collection.find()

# 準備寫入 .asc 檔案
with open("point_cloud_data.asc", "w") as file:
    # 寫入標頭（如果需要）
    file.write("x y z r g b\n")
    
    for document in cursor:
        x = document['x']
        y = document['y']
        z = document['z']
        r = document['r']
        g = document['g']
        b = document['b']
        
        # 寫入點雲資料
        file.write(f"{x} {y} {z} {r} {g} {b}\n")

print("Data has been written to point_cloud_data.asc")
