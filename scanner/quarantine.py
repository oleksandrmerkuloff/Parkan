import os
import json
import platform
import shutil

from cryptography.fernet import Fernet


class Quarantine:
    def __init__(self) -> None:
        self.quarantine_dir = "quarantine"
        self.original_file_paths = {}

        self.ensure_directory_exists(self.quarantine_dir)
        self.load_original_paths()

        self.encryption_key = self.load_or_generate_key()

    def load_or_generate_key(self):
        key_path = "encryption_key.key"
        if os.path.exists(key_path):
            with open(key_path, "rb") as key_file:
                return key_file.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as key_file:
                key_file.write(key)
            return key

    def encrypt_file(self, file_path):
        cipher = Fernet(self.encryption_key)
        with open(file_path, "rb") as file:
            file_data = file.read()
        encrypted_data = cipher.encrypt(file_data)
        with open(file_path, "wb") as file:
            file.write(encrypted_data)
        print(f"File {file_path} encrypted.")

    def decrypt_file(self, file_path):
        cipher = Fernet(self.encryption_key)
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
        print(f"File {file_path} decrypted.")

    def disable_execution(self, file_path):
        if platform.system() != "Windows":
            os.chmod(file_path, 0o600)
        print(f"Execution permissions removed for {file_path}.")

    def restore_execution(self, file_path):
        if platform.system() != "Windows":
            os.chmod(file_path, 0o700)  # Відновити повні дозволи для власника
        print(f"Execution permissions restored for {file_path}.")

    def ensure_directory_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        # Додаємо прихований атрибут для Windows
        if platform.system() == "Windows":
            os.system(f'attrib +h {path}')

    def move_to_quarantine(self, file_path):
        try:
            quarantine_path = os.path.join(self.quarantine_dir, os.path.basename(file_path))
            self.original_file_paths[quarantine_path] = file_path  # Зберігаємо оригінальний шлях
            self.save_original_paths()  # Зберегти словник шляхів у файл
            shutil.move(file_path, quarantine_path)
            print(f"File {file_path} moved to quarantine.")
            self.encrypt_file(quarantine_path)  # Шифрування файлу
            self.disable_execution(quarantine_path)  # Заборона виконання файлу
            return True
        except Exception as e:
            print(f"Failed to move {file_path} to quarantine: {e}")
            return None

    def restore_from_quarantine(self, quarantine_path):
        try:
            original_path = self.original_file_paths.get(quarantine_path)
            if original_path:
                self.decrypt_file(quarantine_path)  # Розшифрування файлу
                shutil.move(quarantine_path, original_path)
                self.restore_execution(original_path)  # Відновлення дозволів на виконання
                print(f"File restored to {original_path}")
                del self.original_file_paths[quarantine_path]
                self.save_original_paths()  # Оновити файл з шляхами
            else:
                print(f"Original path for {quarantine_path} not found.")
        except Exception as e:
            print(f"Failed to restore file from quarantine: {e}")

    def save_original_paths(self):
        with open("original_paths.json", "w") as f:
            json.dump(self.original_file_paths, f)

    def load_original_paths(self):
        if os.path.exists("original_paths.json"):
            with open("original_paths.json", "r") as f:
                self.original_file_paths = json.load(f)

    def delete_quarantine_file(self, file_name):
        try:
            full_path = os.path.join(self.quarantine_dir, file_name)
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"File {file_name} deleted from quarantine.")
                del self.original_file_paths[full_path]  # Видалити з словника шляхів
                self.save_original_paths()  # Оновити файл з шляхами
            else:
                print(f"File {file_name} not found in quarantine.")
        except Exception as e:
            print(f"Failed to delete {file_name}: {e}")
