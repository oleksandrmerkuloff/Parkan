import sqlite3

from get_and_clean import DataCleaner


foreing_databases = {
    "file_types": "type_name",
    "mime_types": "mime_name",
    "signatures": "signature"
}


class DBExtender:
    def __init__(self, db_path) -> None:
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")

        self.data = DataCleaner().delivery()

    def write_foreign_tables(self) -> None:
        foreing_data = [
            list(set(self.data["file_type_guess"].to_dict().values())),
            list(set(self.data["mime_type"].to_dict().values())),
            list(set(self.data["signature"].to_dict().values())),
        ]
        data_index = 0
        for key, value in foreing_databases.items():
            query = f"INSERT INTO {key} ({value}) VALUES (?)"
            data_to_insert = [(item, ) if item else ("unknown", ) for item in foreing_data[data_index]]

            self.cursor.executemany(query, data_to_insert)
            data_index += 1
        self.connection.commit()

    def write_hash_data(self):
        query = "INSERT INTO hashes (date, sha256, sha1, md5, file_type_id, mime_id, signature_id) VALUES (?, ?, ?, ?, ?, ?, ?);"

        for index, row in self.data.iterrows():
            print(index)
            current_file_type = row["file_type_guess"]
            file_type_id = self.find_id("file_types", "type_name", current_file_type)
            if not file_type_id:
                self.cursor.execute("INSERT INTO file_types (type_name) VALUES (?)", (current_file_type,))
                self.connection.commit()
                file_type_id = self.cursor.execute("SELECT MAX(id) FROM file_types").fetchone()[0]
            else:
                file_type_id = file_type_id[0]
            current_mime = row["mime_type"]
            mime_id = self.find_id("mime_types", "mime_name", current_mime)
            if not mime_id:
                self.cursor.execute("INSERT INTO mime_types (mime_name) VALUES (?)", (current_mime,))
                self.connection.commit()
                mime_id = self.cursor.execute("SELECT MAX(id) FROM mime_types").fetchone()[0]
            else:
                mime_id = mime_id[0]
            current_signature = row["signature"]
            signature_id = self.find_id("signatures", "signature", current_signature)
            if not signature_id:
                self.cursor.execute("INSERT INTO signatures (signature) VALUES (?)", (current_signature,))
                self.connection.commit()
                signature_id = self.cursor.execute("SELECT MAX(id) FROM signatures").fetchone()[0]
            else:
                signature_id = signature_id[0]
            data_to_db = (
                row['# "first_seen_utc"'],
                row["sha256_hash"],
                row["sha1_hash"],
                row["md5_hash"],
                file_type_id,
                mime_id,
                signature_id
            )
            self.cursor.execute(query, data_to_db)
        self.connection.commit()

    def find_id(self, table, column, data):
        id_query = f"SELECT id FROM {table} WHERE {column} == (?);"
        index = self.cursor.execute(id_query, (data,)).fetchone()
        return index


if __name__ == "__main__":
    extend_db = DBExtender(r"db_handlers\parkan.db")
    extend_db.write_hash_data()
