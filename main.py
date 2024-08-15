import customtkinter
from customtkinter import CTkImage

import os
from tkinter import filedialog
from tkinter.ttk import Treeview
from PIL import Image

from scanner.scanner import DirectoryScanner
from db_handlers.handlers import PasswordManagerHandler


BASE_DIR = os.path.dirname(__file__)

DB_PATH = r"db_handlers\parkan.db"
hash_column = 'sha256'
table_name = 'hashes'
PASSWORD_TABLE = "passwords"


def clear_frame(frame):
    for widgets in frame.winfo_children():
        widgets.destroy()


class HomeWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Parkan")
        self.iconbitmap(r"images\logo4.ico")
        self.mode = "light"
        self.geometry("720x480")
        self.resizable(False, False)

        # toplevel_windows
        self.scan_window = None

        # add widgets
        self.menu_frame = customtkinter.CTkFrame(
            self,
            width=200,
            height=480,
            fg_color=["gray95", "gray10"]
        )
        self.menu_frame.grid(row=0, column=0, padx=(5, 0), sticky="nsew")

        home_btn = customtkinter.CTkButton(self.menu_frame,
                                           width=150,
                                           height=100,
                                           text="Home",
                                           command=self.to_home,
                                           font=("Franklin Gothic", 24)
                                           )
        home_btn.grid(row=0, column=0, pady=(10, 0), padx=(20, 20))

        scanner_btn = customtkinter.CTkButton(self.menu_frame,
                                              width=150,
                                              height=100,
                                              text="Scanner",
                                              command=self.to_scanner,
                                              font=("Franklin Gothic", 24)
                                              )
        scanner_btn.grid(row=1, column=0, pady=(20, 0), padx=(20, 20))

        quarantine_btn = customtkinter.CTkButton(self.menu_frame,
                                                 width=150,
                                                 height=100,
                                                 text="Quarantine",
                                                 command=self.to_quarantine,
                                                 font=("Franklin Gothic", 24)
                                                 )
        quarantine_btn.grid(row=2, column=0, pady=(20, 0), padx=(20, 20))

        password_manager_btn = customtkinter.CTkButton(self.menu_frame,
                                                       width=150,
                                                       height=100,
                                                       text="Password\nManager",
                                                       command=self.to_password_manager,
                                                       font=("Franklin Gothic", 24)
                                                       )
        password_manager_btn.grid(row=3, column=0, pady=(20, 10), padx=(20, 20))

        self.content_frame = customtkinter.CTkFrame(
            self,
            width=520,
            height=480,
            fg_color=["gray95", "gray10"]
        )
        self.content_frame.grid(row=0, column=1, ipady=300, ipadx=100)

        self.to_home()

    def to_home(self):
        clear_frame(self.content_frame)
        image = CTkImage(Image.open(r"images\dark.png"),
                         Image.open(r"images\light.png"))
        self.mode_btn = customtkinter.CTkButton(
            self.content_frame,
            command=self.change_mode,
            image=image,
            text="",
            width=20,
            fg_color=["gray95", "gray10"]
        )
        self.mode_btn.grid(row=1, column=0, padx=(400, 0), pady=(0, 150))

        header = customtkinter.CTkLabel(
            self.content_frame,
            text="Welcome to Parkan!",
            font=("Franklin Gothic", 36)
            )
        header.grid(row=1, column=0, pady=(120, 60))

        with open("test.txt") as file:
            text = file.read()
        some_content = customtkinter.CTkLabel(self.content_frame, text=text)
        some_content.grid(row=2, column=0, padx=50)

    def to_password_manager(self):
        clear_frame(self.content_frame)
        password_manager = PasswordManagerWidget(self.content_frame)

    def to_scanner(self):
        clear_frame(self.content_frame)

        with open("test.txt") as file:
            text = file.read()
        description = customtkinter.CTkLabel(
            self.content_frame,
            text=text
            )
        description.grid(row=0, column=0, columnspan=3, rowspan=2, padx=(50, 0), pady=(150, 50))

        self.full_scan_btn = customtkinter.CTkButton(
            self.content_frame,
            text="Full scan",
            command=self.scan_process,
            font=("Franklin Gothic", 18),
            height=40
        )
        self.full_scan_btn.grid(row=2, column=0)

        self.selective_scan_btn = customtkinter.CTkButton(
            self.content_frame,
            text="Select folder",
            command=lambda: self.scan_process(1),
            font=("Franklin Gothic", 18),
            height=40
        )
        self.selective_scan_btn.grid(row=2, column=2)

    def scan_process(self, scan_index=0):
        scan_info_window = None
        directory_path = None
        if scan_index:
            directory_path = filedialog.askdirectory(
                initialdir=BASE_DIR,
                title="Select a folder"
                )
        if directory_path:
            if self.scan_window is None or not self.scan_window.winfo_exists():
                self.scan_window = ScanProgressWindow(self)
            else:
                self.scan_window.focus()

            scnned_data = self.scan_window.start_scanning(directory_path)

            if scan_info_window is None or not scan_info_window.winfo_exists():
                scan_info_window = ScanWindowInfo(self, scnned_data)
            else:
                scan_info_window.focus()

    def to_quarantine(self):
        clear_frame(self.content_frame)

        table = Treeview(
            self.content_frame,
            columns=("date", "file_path", "size"),
            show="headings",
            )
        table.column("date", width=50)
        table.column("file_path", width=135)
        table.column("size", width=15)
        table.heading("date", text="Date")
        table.heading("file_path", text="File")
        table.heading("size", text="File Size")
        table.grid(row=0, column=0, padx=20, pady=20, ipadx=130, ipady=80)

    def change_mode(self):
        if self.mode == "light":
            self.mode = "dark"
        elif self.mode == "dark":
            self.mode = "light"
        customtkinter.set_appearance_mode(self.mode)


class ScanProgressWindow(customtkinter.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.test_data_length = 100000

        # window config
        self.geometry("400x200")
        self.config(
            pady=30
        )

        # scanner
        self.scanner = DirectoryScanner(DB_PATH)

        self.cancel_btn = customtkinter.CTkButton(
            self,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_btn.grid(
            row=2,
            column=2,
            pady=(30, 0),
            padx=(0, 20),
            sticky="es")

    def start_scanning(self, directory_path):
        if directory_path:
            scan_data = self.scanner.scan_specific_directory(directory_path, self)
        else:
            scan_data = self.scanner.scan_all_directories(self)

        self.destroy()

        return scan_data

    def cancel(self):
        return self.destroy()


class ScanWindowInfo(customtkinter.CTkToplevel):
    def __init__(self, master, scan_data, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.geometry("400x200")

        time_label = customtkinter.CTkLabel(
            self,
            text=f"Spend time: {scan_data[0]}"
        )
        time_label.grid(row=0, column=0)

        files_label = customtkinter.CTkLabel(
            self,
            text=f"Files scanned: {scan_data[1]}"
        )
        files_label.grid(row=1, column=0)


class PasswordManagerWidget:
    def __init__(self, master) -> None:
        self.db_handler = PasswordManagerHandler(DB_PATH)
        self.update_window = None
        self.table = "passwords"
        self.master = master

        password_urls = self.db_handler.get_urls("website", self.table)

        self.password_menu_frame = customtkinter.CTkScrollableFrame(
            self.master,
            width=160,
            height=480,
            fg_color=["gray95", "gray10"]
            )
        self.password_menu_frame.grid(
            row=0, column=0, sticky="nsew", padx=(0, 20), ipadx=5
        )

        self.password_frame = PasswordFrame(
            self.master,
            fg_color=["gray95", "gray10"],
            widget=self
            )
        self.password_frame.grid(row=0, column=1)

        self.add_password_btn = customtkinter.CTkButton(
            self.password_menu_frame,
            text="Add new",
            width=150,
            height=30,
            command=self.password_frame.create_password_form,
            font=("Bahnschrift", 18)
        )
        self.add_password_btn.grid(row=0, column=0, pady=(50, 10))

        row_id = 1
        for id, url in password_urls:
            password_btn = customtkinter.CTkButton(
                self.password_menu_frame,
                text=url,
                width=150,
                height=30,
                command=lambda id=id: self.password_frame.create_password_form(id),
                font=("Bahnschrift", 16)
            )
            password_btn.grid(row=row_id, column=0, pady=(10, 10))
            row_id += 1

    def reset(self):
        self.__init__(self.master)


class PasswordFrame(customtkinter.CTkFrame):
    def __init__(self, master, widget, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.width = 360,
        self.height = 480
        self.widget = widget

        self.db_handler = PasswordManagerHandler(DB_PATH)

        self.create_password_form()

    def create_password_form(self, id=None):
        clear_frame(self)

        website_label = customtkinter.CTkLabel(
            self,
            text="Enter website url:",
            font=("Bahnschrift", 24)
        )
        website_label.grid(row=0, column=0, padx=(60, 30), pady=(50, 20))
        self.website_entry = customtkinter.CTkEntry(
            self,
            width=220,
            font=("Franklin Gothic", 18)
        )
        self.website_entry.grid(row=1,
                                column=0,
                                columnspan=2,
                                padx=(50, 30))

        login_label = customtkinter.CTkLabel(
            self,
            text="Enter Login:",
            font=("Bahnschrift", 24)
        )
        login_label.grid(row=2, column=0, padx=(0, 30), pady=(40, 20))
        self.login_entry = customtkinter.CTkEntry(
            self,
            width=220,
            font=("Franklin Gothic", 18)
        )
        self.login_entry.grid(row=3,
                              column=0,
                              columnspan=2,
                              padx=(50, 30))

        password_label = customtkinter.CTkLabel(
            self,
            text="Enter Password:",
            font=("Bahnschrift", 24)
        )
        password_label.grid(row=4, column=0, padx=(50, 30), pady=(40, 20))
        self.password_entry = customtkinter.CTkEntry(
            self,
            width=220,
            font=("Franklin Gothic", 18)
        )
        self.password_entry.grid(row=5,
                                 column=0,
                                 columnspan=2,
                                 padx=(50, 30))

        if id:
            password_data = self.db_handler.get_data_by_id(id, PASSWORD_TABLE)
            self.website_entry.insert(0, password_data[1])
            self.login_entry.insert(0, password_data[2])
            self.password_entry.insert(0, password_data[3])

            delete_btn = customtkinter.CTkButton(
                self,
                width=75,
                height=40,
                text="Delete",
                font=("Franklin Gothic", 20),
                command=lambda id=id: self.delete(id)
            )

            update_btn = customtkinter.CTkButton(
                self,
                width=70,
                height=40,
                text="Update",
                font=("Franklin Gothic", 20),
                command=lambda id=id: self.update(id)
            )

            update_btn.grid(row=6, column=0, pady=(25, 15), padx=(160, 0))
            delete_btn.grid(row=6, column=0, pady=(25, 15), padx=(0, 100))
        else:
            add_password_btn = customtkinter.CTkButton(
                self,
                text="Save",
                font=("Franklin Gothic", 20),
                width=220,
                command=self.add_new_record
            )
            add_password_btn.grid(row=6, column=0, pady=(25, 0), padx=(30, 0))

    def collect_data(self):
        url = self.website_entry.get()
        login = self.login_entry.get()
        password = self.password_entry.get()
        data = (url, login, password)
        return data

    def add_new_record(self):
        data = self.collect_data()
        self.db_handler.insert_record(PASSWORD_TABLE, data)
        self.widget.reset()

    def delete(self, id):
        self.db_handler.delete_record(id=id, table=PASSWORD_TABLE)
        self.widget.reset()

    def update(self, id):
        data = self.collect_data()
        self.db_handler.update_record(PASSWORD_TABLE, id, data)
        self.widget.reset()


if __name__ == "__main__":
    window = HomeWindow()
    window.mainloop()
