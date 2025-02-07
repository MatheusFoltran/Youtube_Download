from typing import Callable
import customtkinter
import tkinter as tk
import os
from PIL import Image
from pathlib import Path
import sys
import json

from downloader import download

FOLDER_PATH =  str(Path(Path(__file__).parent.absolute()))
sys.path.insert(0, FOLDER_PATH)

CONFIG_PATH = os.path.join(FOLDER_PATH, "config.json")


class GUI(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()

        # Change icon
        self.iconbitmap(os.path.join(FOLDER_PATH, "UI_images", "program_icon.ico"))

        self.configs = None
        self.get_configs()
        self.create_ui()
    
    def create_ui(self) -> None:
        self.title("Pytube Downloader")
        self.geometry("700x450")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.callbacks = {}

        self.home_frame = HomeFrame(self)
        self.settings_frame = SettingsFrame(self)
        self.navigation_frame = NavigationFrame(self)
    
    # Read configs from json file
    def get_configs(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as json_file:
                self.configs = json.load(json_file)
        else:
            self.configs = {}
            self.configs['default_download_folder'] = None


class NavigationFrame(customtkinter.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)
    
        # load images with light and dark mode image
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "UI_images")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "program_image.jpg")), size=(26, 26))
        self.home_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "home_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "home_light.png")), size=(20, 20))
        self.calendar_image = customtkinter.CTkImage(light_image=Image.open(os.path.join(image_path, "settings_dark.png")),
                                                 dark_image=Image.open(os.path.join(image_path, "settings_light.png")), size=(20, 20))
        

        # Create navigation frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self, text="  Pytube Downloader", image=self.logo_image,
                                                             compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.home_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Home",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   image=self.home_image, anchor="w", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.settings_button = customtkinter.CTkButton(self, corner_radius=0, height=40, border_spacing=10, text="Settings",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      image=self.calendar_image, anchor="w", command=self.settings_button_event)
        self.settings_button.grid(row=2, column=0, sticky="ew")

        self.appearance_mode_menu = customtkinter.CTkOptionMenu(self, values=["Dark", "Light", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Select default frame
        self.select_frame_by_name("home")

    def select_frame_by_name(self, name):
        # Set button color for selected button
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "calendar" else "transparent")

        # Show selected frame
        if name == "home":
            self.master.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.master.home_frame.grid_forget()
        if name == "settings":
            self.master.settings_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.master.settings_frame.grid_forget()

    def home_button_event(self):
        self.select_frame_by_name("home")

    def settings_button_event(self):
        self.select_frame_by_name("settings")
    
    def change_appearance_mode_event(self, new_appearance_mode):
        customtkinter.set_appearance_mode(new_appearance_mode)
    

class HomeFrame(customtkinter.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.configs = self.master.configs
        self.folder = self.configs['default_download_folder']
        self.create_ui()    

    def create_ui(self) -> None:
        self.folder_button = customtkinter.CTkButton(
            self,
            text="Choose folder",
            width=300,
        )

        self.folder_path = customtkinter.CTkLabel(
            self,
            text=f"Current folder: {self.folder}",
            width=300,
            font=customtkinter.CTkFont("Arial", 15),
            height=25,
            corner_radius=8
        )

        self.bind_choose_folder(self.choose_folder)

        self.folder_path.pack(side=tk.TOP, anchor=tk.CENTER, pady=10, fill=tk.X)
        self.folder_button.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)

        self.url = customtkinter.CTkEntry(self, width=300, placeholder_text="Enter URL here")

        self.radio_var = tk.IntVar(value=0)
        self.radiobutton_audio = customtkinter.CTkRadioButton(self, text="Download Audio",
                                                    command=self.radiobutton_event, variable=self.radio_var, value=1)
        self.radiobutton_video = customtkinter.CTkRadioButton(self, text="Download Video",
                                                    command=self.radiobutton_event, variable=self.radio_var, value=2)

        self.download_button = customtkinter.CTkButton(
            self,
            text="Download",
            width=300,
        )

        self.check_download_conditions()
        self.bind_download_button(self.download)

        self.url.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)
        self.radiobutton_video.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
        self.radiobutton_audio.pack(side=tk.TOP, anchor=tk.CENTER, pady=5)
        self.download_button.pack(side=tk.TOP, anchor=tk.CENTER, pady=10)

    def choose_folder(self, event):
        self.folder = tk.filedialog.askdirectory()
        self.folder_path.configure(text=f"Current folder: {self.folder}")
        self.check_download_conditions()

    def download(self, event):
        download(self.url.get(), self.folder, audio_only=self.audio_only)
        # self.url.delete(0, tk.END)

    def bind_choose_folder(self, method: Callable[[tk.Event], None]) -> None:
        self.folder_button.bind("<Button-1>", method)
    
    def bind_download_button(self, method: Callable[[tk.Event], None]) -> None:
        self.download_button.bind("<Button-1>", method)
    
    def radiobutton_event(self):
        if self.radio_var.get() == 1:
            self.audio_only = True
        elif self.radio_var.get() == 2:
            self.audio_only = False
        else:
            raise ValueError("Invalid value for radiobutton")

        self.check_download_conditions()

        print("radiobutton toggled, current value:", self.radio_var.get())
        print(f"audio_only = {self.audio_only}")
    
    def check_download_conditions(self):
        if self.folder is None or self.radio_var.get() == 0:
            self.download_button.configure(state=tk.DISABLED)
        else:
            self.download_button.configure(state=tk.NORMAL)


class SettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.folder = None
        self.configs = self.master.configs
        self.create_ui()
        self.get_configs()

    def create_ui(self) -> None:

        # Create settings frame
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)

        # Define default download folder
        self.default_download_folder = customtkinter.CTkEntry(self, width=300, placeholder_text="Enter default download folder")
        self.folder_button = customtkinter.CTkButton(
            self,
            image=customtkinter.CTkImage(light_image=Image.open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "UI_images", "folder_dark.png"))),
            text="",
            width=50,
        )
        
        self.bind_choose_folder(self.choose_folder)

        self.default_download_folder.grid(row=0, column=0, padx=20, pady=20)
        self.folder_button.grid(row=0, column=1, padx=20, pady=20)

        # Define save button
        self.save_button = customtkinter.CTkButton(
            self,
            text="Save",
            width=300,
        )

        self.bind_save_button(self.save_to_json)

        self.save_button.grid(row=4, column=0, sticky='WE', padx=20, pady=20, columnspan=2)
    
    def get_configs(self):
        self.default_download_folder.insert(0, f"{self.configs['default_download_folder']}")

    # Save data to a json file
    def save_to_json(self, event):
        data = {}
        data['default_download_folder'] = self.default_download_folder.get()
        with open(CONFIG_PATH, 'w') as outfile:
            json.dump(data, outfile)

    def choose_folder(self, event):
        self.folder = tk.filedialog.askdirectory()
        self.default_download_folder.delete(0, tk.END)
        self.default_download_folder.insert(0, f"{self.folder}")

    def bind_choose_folder(self, method: Callable[[tk.Event], None]) -> None:
        self.folder_button.bind("<Button-1>", method)
    
    def bind_save_button(self, method: Callable[[tk.Event], None]) -> None:
        self.save_button.bind("<Button-1>", method)


