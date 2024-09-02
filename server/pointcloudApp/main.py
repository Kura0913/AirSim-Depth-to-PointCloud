from JsonFileHandler import JsonFileHandler
import keyboard
import threading
from AppCommand.DepthConverter import DepthConverter
from AppCommand.PointcloudConverter import PointcloudConverter
from watchdog.observers import Observer
from DBController.SqliteDBConnection import DBConnection
from DBController.SqliteDBInitializer import DBInitializer
from DBController.MysqlDBInitializer import MysqlDBInitializer
from DBController.MysqlPointCloudInfoTable import MysqlPointCloudInfoTable


stop_event = threading.Event()

func_dict = {
    1: DepthConverter(),
    2: PointcloudConverter()
}

# waiting for pressing 'p' key to stop
def listen_for_stop():
    keyboard.wait('p')
    stop_event.set()

def show_menu():
    print("==============================")
    print("1: Depth images to point cloud, and converted to world coordinates.")
    print("2: Convert point cloud data to world coordinates.")
    print("3: Clear processed files list.")
    print("4: Clear point clouds data in DB.")
    print("5: Close app.")
    print("==============================")
    try:
        selection = int(input("Select function:"))
        if selection not in [1, 2, 3, 4, 5]:
            raise ValueError
    except ValueError:
        print("Please input with 1~5.")
        return 0

    return selection

def clear_processed_files():
    with open('processed_files.txt', 'w') as file:
        file.write('')
    print("Processed files list has been cleared.")

def main():
    stop_event = threading.Event()
    stop_thread = threading.Thread(target=listen_for_stop)
    stop_thread.start()
    # connect to sqlite
    DBConnection.db_file_path = "../vehicle_info.db"
    DBInitializer().execute()
    # connect to mysql
    mysql_db = MysqlDBInitializer()
    mysql_db.execute()
    # initial selection
    selection = 0

    # start app
    while not stop_event.is_set():
        while selection == 0 and not stop_event.is_set():
            selection = show_menu()

        if selection == 5:  # Exit option selected
            break
        elif selection == 3:
            clear_processed_files()
        elif selection == 4:
            MysqlPointCloudInfoTable().delete_all_points()
        elif selection == 1:
            json_path = "../json_file/depth/"
            processor = func_dict[1]
        elif selection == 2:
            json_path = "../json_file/pointcloud/"
            processor = func_dict[2]
        # 創建對應的JSON文件處理器
        if selection in [1, 2]:
            event_handler = JsonFileHandler(json_path, processor)
            observer = Observer()
            observer.schedule(event_handler, json_path, recursive=False)

            # 先處理已存在的文件
            event_handler.process_existing_files()

            # 開始監控新的文件
            observer.start()
            print(f"Started processing JSON files in: {json_path}")

            # 等待stop_event觸發
            while not stop_event.is_set():
                pass

            # 停止觀察者
            observer.stop()
            observer.join()
            print("Stopped processing.")

        # 重置選擇
        selection = 0

    stop_event.set()
    stop_thread.join()

if __name__ == "__main__":
    main()


