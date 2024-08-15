from Cryptodome.Hash import SHA256
from Cryptodome.Protocol.KDF import PBKDF2


class Manager:
    def __init__(self) -> None:
        try:
            self.open_root_password()
        except FileNotFoundError:
            new_root_file = input("Hmm, seems you are not create your password, enter new here: ")
            self.write_root_password(new_root_file)
        finally:
            if self.check_user():
                print("Access allowed")
            else:
                print("Get fucking off from my data!")

    def open_root_password(self):
        with open("root_password.bin", "rb") as file:
            password = file.read(32)
        return password

    def check_user(self):
        user_password = input("Enter your password")
        user_password = self.create_root_password_hash(user_password)
        root_password = self.open_root_password()
        if root_password == user_password:
            return True
        else:
            return False

    def create_root_password_hash(self, password):
        salt = b'\x1c\xc5\xc2Zd\x95\xff\xf4Z\xd2\xc4o2\xfe\xe4\x94\x1e\xc9\x9f\xb4\x958\xa6\xaf@i\xccVh+\x8dR'
        count = 1_000_000
        key = PBKDF2(password, salt, 32, count)
        root_password_hash = SHA256.new(key)
        return root_password_hash.digest()

    def write_root_password(self, password):
        hash_password = self.create_root_password_hash(password)
        with open("root_password.bin", "wb") as file:
            file.write(hash_password)

    def add_password(self, website_link, password, notes=""):
        password_id = len(self.data)
        self.data[password_id] = {
            "website": website_link,
            "password": self.encrypt_password(password),
            "notes": notes
        }


if __name__ == "__main__":
    root_password = "I am Crystal1s motherf#ckers"
    t = Manager()
