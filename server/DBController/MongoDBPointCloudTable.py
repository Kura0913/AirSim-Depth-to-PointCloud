from DBController.MongoDBConnection import MongoDBConnection
from concurrent.futures import ThreadPoolExecutor
from pymongo import UpdateOne

class MongoDBPointCloudTable:
    def __init__(self, collection_name="point_cloud_info"):
        self.collection_name = collection_name    

    def upsert_point_clouds_with_color(self, point_cloud_info, color_info, batch_size=1000, max_workers=40):
        if len(point_cloud_info) != len(color_info):
            print("The number of coordinates and colors must match.")
            return 

        total_operations = len(point_cloud_info)
        batches = [(start, min(start + batch_size, total_operations)) for start in range(0, total_operations, batch_size)]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(lambda batch: self._process_batch(batch, point_cloud_info, color_info), batches)

        # total_matched = total_modified = total_upserted = 0
        # for result in results:
        #     total_matched += result["matched"]
        #     total_modified += result["modified"]
        #     total_upserted += result["upserted"]

        # print(f"Total Matched: {total_matched}, Modified: {total_modified}, Upserted: {total_upserted}")
        
    def _process_batch(self, batch, point_cloud_info, color_info):
        start, end = batch
        operations = []
        for idx in range(start, end):
            point = {
                "x": point_cloud_info[idx][0],
                "y": point_cloud_info[idx][1],
                "z": point_cloud_info[idx][2]                
            }

            update_operation = {
                "$set": {
                    "r": color_info[idx][0],
                    "g": color_info[idx][1],
                    "b": color_info[idx][2]
                }
            }

            operations.append(
                UpdateOne(point, update_operation, upsert=True)
            )

        if operations:
            with MongoDBConnection() as db:
                collection = db[self.collection_name]
                try:
                    result = collection.bulk_write(operations)
                    return {
                        "matched": result.matched_count,
                        "modified": result.modified_count,
                        "upserted": result.upserted_count
                    }
                except Exception as e:
                    print("Failed to perform bulk upsert operation.")
                    print(e)
                    return {"matched": 0, "modified": 0, "upserted": 0}
        return {"matched": 0, "modified": 0, "upserted": 0}
    
    def update_pointcloud(self, filter, update_data):
        with MongoDBConnection() as db:
            collection = db[self.collection_name]
            try:
                collection.update_many(filter, {'$set': update_data})
                print("Point cloud data updated successfully.")
            except Exception as e:
                print("Failed to update point cloud data.")
                print(e)

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