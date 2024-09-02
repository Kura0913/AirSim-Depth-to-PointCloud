import os
import json
from watchdog.events import FileSystemEventHandler


# 假設使用一個文件來存已處理過的文件名
PROCESSED_FILES_RECORD = "processed_files.txt"


class JsonFileHandler(FileSystemEventHandler):
    def __init__(self, directory_to_watch, processor):
        """
        directory_to_watch: 監控的JSON檔案目錄
        processor: 負責處理JSON檔案的處理類別實例
        """
        self.directory_to_watch = directory_to_watch
        self.processor = processor
        self.processed_files = self.load_processed_files()

    def load_processed_files(self):
        """載入已處理過的文件名稱"""
        if os.path.exists(PROCESSED_FILES_RECORD):
            with open(PROCESSED_FILES_RECORD, 'r') as f:
                return set(f.read().splitlines())
        return set()

    def save_processed_file(self, filename):
        """保存已處理文件的名稱"""
        with open(PROCESSED_FILES_RECORD, 'a') as f:
            f.write(filename + "\n")
        self.processed_files.add(filename)

    def process_file(self, filepath):
        """處理JSON文件"""
        with open(filepath, 'r') as file:
            parameters = json.load(file)
        # 調用對應的處理類別進行處理
        self.processor.execute(parameters)
        # 標記文件已處理
        self.save_processed_file(os.path.basename(filepath))

    def on_created(self, event):
        """監聽新文件創建事件"""
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        if filename not in self.processed_files:
            self.process_file(filepath)

    def process_existing_files(self):
        """處理目錄中已存在的文件"""
        for filename in os.listdir(self.directory_to_watch):
            if filename.endswith(".json") and filename not in self.processed_files:
                self.process_file(os.path.join(self.directory_to_watch, filename))