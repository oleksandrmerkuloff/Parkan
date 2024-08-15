import sqlite3


class BaseDBHandler:
    def __init__(self, db_path: str) -> None:
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

    def get_all_data(self, table: str) -> list:
        self.cursor.execute(f"SELECT * FROM {table}")
        data = self.cursor.fetchall()
        return data

    def get_data_by_id(self, id: int, table: str) -> tuple:
        self.cursor.execute(f"SELECT * FROM {table} WHERE id = {id}")
        record = self.cursor.fetchone()
        return record

    def get_data_by_column(self, column: str, table: str) -> list:
        self.cursor.execute(f"SELECT {column} FROM {table}")
        column_data = self.cursor.fetchall()
        return column_data

    def delete_record(self, id: int, table: str) -> None:
        self.cursor.execute(f"DELETE FROM {table} WHERE id = ?", (id,))
        self.connection.commit()


class PasswordManagerHandler(BaseDBHandler):
    def insert_record(self, table, data: tuple) -> None:
        query = f"INSERT INTO {table}(website, login, password) VALUES (?, ?, ?)"
        self.cursor.execute(query, data)
        self.connection.commit()

    def get_urls(self, column: str, table: str) -> list:
        self.cursor.execute(f"SELECT id, {column} FROM {table}")
        column_data = self.cursor.fetchall()
        return column_data

    def update_record(self, table, id: str, new_data: tuple) -> None:
        query = f"UPDATE {table} SET website = ?, login = ?, password = ? WHERE id = {id}"
        self.cursor.execute(query, new_data)
        self.connection.commit()


# class MalwareHandler(BaseDBHandler):
#     def __init__(self, db_path: str) -> None:
#         super().__init__(db_path)
#         pass
