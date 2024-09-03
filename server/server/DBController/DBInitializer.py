from DBController.DBConnection import DBConnection


necessary_table_to_create = {
    "point_cloud_info":
    """
        CREATE TABLE IF NOT EXISTS point_cloud_info
        (
            point_id INT AUTO_INCREMENT PRIMARY KEY,
            point_x FLOAT,
            point_y FLOAT,
            point_z FLOAT,
            color_r FLOAT,
            color_g FLOAT,
            color_b FLOAT,
            UNIQUE(point_x, point_y, point_z)
        );
    """,
    "drone_info":
    """
        CREATE TABLE IF NOT EXISTS drone_info
        (
            drone_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL
        )
    """,
    "camera_info":
    """
            CREATE TABLE IF NOT EXISTS camera_info
            (
                drone_id INT,
                camera_face INT,
                translation_x FLOAT,
                translation_y FLOAT,
                translation_z FLOAT,
                quaternion_w FLOAT,
                quaternion_x FLOAT,
                quaternion_y FLOAT,
                quaternion_z FLOAT,
                fov FLOAT,
                width INT,
                height INT
            )
    """,
    "lidar_info":
    """
            CREATE TABLE IF NOT EXISTS lidar_info
            (
                drone_id INT,
                lidar_face INT,
                translation_x FLOAT,
                translation_y FLOAT,
                translation_z FLOAT,
                quaternion_w FLOAT,
                quaternion_x FLOAT,
                quaternion_y FLOAT,
                quaternion_z FLOAT
            )
    """
}


class DBInitializer:
    def execute(self):
        existing_tables = self.get_existing_tables()
        self.create_not_exist_table(existing_tables)

    def get_existing_tables(self):
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            records = cursor.fetchall()

        return [single_row[0] for single_row in records]

    def create_not_exist_table(self, existing_tables):
        for necessary_table, table_creating_command in necessary_table_to_create.items():
            if necessary_table not in existing_tables:
                self.create_table_with_specefied_command(table_creating_command)

    def create_table_with_specefied_command(self, command):
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()