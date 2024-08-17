from pymongo import MongoClient

class MongoDBConnection():
    def __init__ (self):
        self.mongodb_client = MongoClient(self.db_uri)
        self.database = self.mongodb_client[self.db_name]

    def __enter__(self):
        return self.database
    
    @classmethod
    def initialize(cls, uri, dbname):
        cls.db_uri = uri
        cls.db_name = dbname

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mongodb_client.close()

    def ping(self):
        try:
            self.mongodb_client.admin.command('ping')
            print("connect success!!")
            return True
        except:
            print("connect faild, please check mongodb uri.")
            return False

    def get_collection(self, collection_name):
        collection = self.database[collection_name]
        return collection

    def find(self, collection_name, filter = {}, limit=0):
        collection = self.database[collection_name]
        items = list(collection.find(filter=filter, limit=limit))
        return items
    
    def index_exists(self, index_fields, collection_name):
        """檢查是否已經存在指定的索引"""
        collection = self.database[collection_name]
        indexes = collection.list_indexes()
        for index in indexes:
            if index['key'] == index_fields:
                return True
            else:
                return False

    def create_indexes(self, collection_name):
        """創建索引（如果尚未創建）"""
        index_fields = [("x", 1), ("y", 1), ("z", 1)]
        if not self.index_exists(dict(index_fields), collection_name):
            collection = self.database[collection_name]
            collection.create_index(index_fields, unique=True)
            print("Indexes created successfully.")
        else:
            print("Index already exists.")