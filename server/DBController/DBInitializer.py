from DBController.DBConnection import DBConnection


necessary_table_to_create = {
    "point_cloud_info":
        """
            CREATE TABLE point_cloud_info
            (
                point_id INTEGER PRIMARY KEY,
                point_x FLOAT,
                point_y FLOAT,
                point_z FLOAT,
                color_r FLOAT,
                color_g FLOAT,
                color_b FLOAT

            );
        """,
    "drone_info":
        """
            CREATE TABLE drone_info
            (
                drone_id INTEGER PRIMARY KEY,
                name VARCHAR(255),
                fov INTEGER,
                image_width INTEGER,
                image_height INTEGER
            )
        """,
    "camera_info":
    """
            CREATE TABLE camera_info
            (
                drone_id INTEGER,
                camera_face INTEGER,
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
            cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
            records = cursor.fetchall()

        return [single_row["tbl_name"] for single_row in records]

    def create_not_exist_table(self, existing_tables):
        for necessary_table, table_creating_command in necessary_table_to_create.items():
            if necessary_table not in existing_tables:
                self.create_table_with_specefied_command(table_creating_command)

    def create_table_with_specefied_command(self, command):
        with DBConnection() as connection:
            cursor = connection.cursor()
            cursor.execute(command)
            connection.commit()