import os
import platform
import hashlib
import sqlite3
import time
from .quarantine import Quarantine
import customtkinter
from tkinter.ttk import Progressbar


class DirectoryScanner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.hash_column = "sha256"
        self.table_name = "hashes"

        self.quarantine = Quarantine()

        self.results = []
        self.matched_files = []

    def get_all_drives(self):
        system = platform.system()
        if system == "Windows":
            return os.listdrives()
        elif system == "Linux" or system == "Darwin":
            return ['/']
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

    #Завантажити всі хеші з бази даних в ОП
    def load_hashes_from_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = f"SELECT {self.hash_column} FROM {self.table_name}"

                cursor.execute(query)

                rows = cursor.fetchall()
                self.hashes_set = set(row[0].strip().lower() for row in rows)
        except sqlite3.DatabaseError as e:
            print(f"Database error: {e}")

    # Обчислення SHA-256 хеш файлу.
    def get_file_hash(self, filepath):
        try:
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest().strip().lower()
        except Exception:
            return None

    # Перевірка, чи є хеш файлу в базі даних.
    def compare_hash_with_db(self, file_hash):
        return file_hash in self.hashes_set

    # Карантин: Обробка файлу для переміщення в карантин
    def process_file(self, file_path):
        file_hash = self.get_file_hash(file_path)
        if file_hash:
            if self.compare_hash_with_db(file_hash):
                quarantine_path = self.quarantine.move_to_quarantine(file_path)

                #? додавання до списку файлів шпз?
                self.matched_files.append(quarantine_path)
            self.results.append(file_path)

    # Сканування всіх файлів директорії.
    #! В майбутньому треба буде розробити свій метод проходження директорій для пришвидшення процесу
    def scan_directory(self, path, total):
        for root, dirs, files in os.walk(path):
            for name in files:
                file_path = os.path.join(root, name)

                self.process_file(file_path)

                self.progress_bar["value"] += 1
                self.file_label.configure(text=f"Done: {self.progress_bar["value"]}/{total}")
                self.progress_bar.master.update()

    #Врахування лише файлів у загальній кількості
    def scan_all_directories(self, master):
        self.results.clear()
        self.matched_files.clear()
        all_drives = self.get_all_drives()
        self.load_hashes_from_db()

        #! Треба змінювати нижній цикл, бо виконання тільки його займає 12с - 30с

        total_items = 0
        for drive in all_drives:
            for _, dirs, files in os.walk(drive):
                total_items += len(files)

        # GUI elements

        self.progress_bar = Progressbar(
            master,
            length=300,
            value=0
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=25)

        self.file_label = customtkinter.CTkLabel(
            master,
            text=f"Items left: 0/{total_items}"
        )
        self.file_label.grid(row=0, column=1, pady=(0, 20))

        self.progress_bar = Progressbar(
            master,
            length=300,
            value=0,
            maximum=total_items
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=25)

        start_time = time.time()
        for drive in all_drives:
            self.scan_directory(drive, total_items)
        end_time = time.time()

        # Результати ПЕРЕРОБИТИ НА ВИВІД У ВІкно
        elapsed_time = end_time - start_time
        processing_speed = total_items / elapsed_time
        print(f"\nTotal files scanned: {total_items}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Processing speed: {processing_speed:.2f} files/second")
        return elapsed_time, total_items

    # Врахування лише файлів у загальній кількості для конкретної директорії
    def scan_specific_directory(self, path, master):
        self.results.clear()
        self.matched_files.clear()
        total_items = sum([len(files) for _, dirs, files in os.walk(path)])
        self.load_hashes_from_db()

        # GUI

        self.file_label = customtkinter.CTkLabel(
            master,
            text=f"Items left: 0/{total_items}"
        )
        self.file_label.grid(row=0, column=1, pady=(0, 20))

        self.progress_bar = Progressbar(
            master,
            length=300,
            value=0,
            maximum=total_items
        )
        self.progress_bar.grid(row=1, column=0, columnspan=3, padx=25)

        # SCAN PROCESS

        start_time = time.time()
        self.scan_directory(path, total_items)
        end_time = time.time()

        # Результати ПЕРЕРОБИТИ НА ВИВІД У ВІкно
        elapsed_time = end_time - start_time
        processing_speed = total_items / elapsed_time
        print(f"\nTotal files scanned: {total_items}")
        print(f"Elapsed time: {elapsed_time:.2f} seconds")
        print(f"Processing speed: {processing_speed:.2f} files/second")
        return elapsed_time, total_items


    #! Формування звіту про результати сканування.
    def generate_report(self):
        total_scanned = len(self.results)
        total_matched = len(self.matched_files)


class DirectoryScannerApp:
    def __init__(self, db_path, hash_column, table_name):
        self.scanner = DirectoryScanner(db_path, hash_column, table_name)

    # Запуск програми для вибору варіанту сканування
    def run(self):
        print("Select an option:")
        print("1. Scan all directories on the computer")
        print("2. Scan a specific directory")

        choice = input("Enter the option number (1 or 2): ")

        if choice == '1':
            self.scanner.scan_all_directories()
            self.scanner.generate_report('scan_report.txt')
            print("Scan report saved to 'scan_report.txt'")
        elif choice == '2':
            path = input("Enter the path of the directory to scan: ")
            if os.path.isdir(path):
                self.scanner.scan_specific_directory(path)
                self.scanner.generate_report('scan_report.txt')
                print("Scan report saved to 'scan_report.txt'")
            else:
                print("The specified path is not a directory or does not exist.")
        else:
            print("Invalid choice. Please try again.")

        self.post_scan_options()

    #!
    #!
    #!
    #!
    #Карантин: Опції після сканування
    def post_scan_options(self):
        quarantine_files = os.listdir(self.scanner.quarantine_dir)
        if not quarantine_files:
            print("No files in quarantine. Exiting.")
            return

        print("\nFiles in quarantine:")
        for i, file_name in enumerate(quarantine_files, 1):
            print(f"{i}. {file_name}")

        print("\nWhat would you like to do with the files in quarantine?")
        print("1. Delete specific files")
        print("2. Restore specific files")

        choice = input("Enter the option number (1 or 2): ")

        if choice == '1':
            self.handle_quarantine_files(quarantine_files, action="delete")
        elif choice == '2':
            self.handle_quarantine_files(quarantine_files, action="restore")
        else:
            print("Invalid choice. Exiting without any actions.")

    #Карантин: Обробка файлів у карантині
    def handle_quarantine_files(self, quarantine_files, action):
        selected_indices = input("Enter the numbers of the files you want to manage (comma-separated): ")
        selected_indices = selected_indices.split(",")

        for index in selected_indices:
            try:
                index = int(index.strip()) - 1
                if index < 0 or index >= len(quarantine_files):
                    print(f"Invalid selection: {index + 1}")
                    continue

                file_name = quarantine_files[index]
                if action == "delete":
                    self.scanner.delete_quarantine_file(file_name)
                elif action == "restore":
                    self.scanner.restore_from_quarantine(os.path.join(self.scanner.quarantine_dir, file_name))
            except ValueError:
                print(f"Invalid input: {index + 1}")

# Приклад запуску сканера
# if __name__ == "__main__":
#     db_path = os.path.join(os.path.dirname(__file__), 'malware.db')
#     hash_column = 'sha256_hash'
#     table_name = 'hashes'
#     app = DirectoryScannerApp(db_path, hash_column, table_name)
#     app.run()
