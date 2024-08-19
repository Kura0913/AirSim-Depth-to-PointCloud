from DBController.MongoDBConnection import MongoDBConnection
from concurrent.futures import ThreadPoolExecutor
from pymongo import InsertOne

class MongoDBPointCloudTable:
    def __init__(self, collection_name="point_cloud_info"):
        self.collection_name = collection_name    

    def Insert_point_clouds_with_color(self, point_cloud_info, color_info, batch_size=1000, max_workers=40):
        if len(point_cloud_info) != len(color_info):
            print("The number of coordinates and colors must match.")
            return 
        
        total_operations = len(point_cloud_info)
        batches = [(start, min(start + batch_size, total_operations)) for start in range(0, total_operations, batch_size)]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._process_batch, batch, point_cloud_info, color_info) for batch in batches]
        
    def _process_batch(self, batch, point_cloud_info, color_info):
        start, end = batch
        operations = []
        for idx in range(start, end):
            point = {
                "x": point_cloud_info[idx][0],
                "y": point_cloud_info[idx][1],
                "z": point_cloud_info[idx][2],
                "r": color_info[idx][0],
                "g": color_info[idx][1],
                "b": color_info[idx][2]
            }

            operations.append(InsertOne(point))

        result = {"inserted": 0, "ignored": 0}
        if operations:
            with MongoDBConnection() as db:
                collection = db[self.collection_name]
                try:
                    result_obj = collection.bulk_write(operations, ordered=False)
                    result["inserted"] = result_obj.inserted_count
                    result["ignored"] = len(result_obj.bulk_api_result["writeErrors"])
                except:
                    pass
        return result

    def export_all_pointcloud(self):
        points = []
        colors = []
        with MongoDBConnection() as db:
            collection = db[self.collection_name]
            try:
                cursor = collection.find()
                for document in cursor:
                    point = [document.get("x"), document.get("y"), document.get("z")]
                    color = [document.get("r"), document.get("g"), document.get("b")]
                    points.append(point)
                    colors.append(color)
                print("Exported all point cloud data.")
                return {"points": points, "colors": colors}
            except Exception as e:
                print("Failed to export point cloud data.")
                print(e)
                return {"points": [], "colors": []}