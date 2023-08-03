import json
import os
from pathlib import Path
from typing import Callable

import customtkinter as ctk


class ImageDirectoryPopOut():
    """
    Pop-out window for selecting the image directory in the Rank-Based 
    Annotation application.
    """

    def __init__(
            self, root: ctk.CTk, center: Callable, save_obj: dict,
            submit_path: Callable, back_to_menu: Callable):
        """
        Initializes the ImageDirectoryPopOut object.

        Args:
            root (CTk): The root cutom tkinter object.
            center (function): A function to center the pop-out window.
            save_obj (dict): The save object containing the sort algorithm and 
            other parameters.
            submit_path (function): A function to submit the selected image 
            directory path.
            back_to_menu (function): A function to go back to the main menu.
        """
        self.root = root
        self.center = center
        self.save_obj = save_obj
        self.submit_path = submit_path
        self.back_to_menu = back_to_menu

        pop_out = ctk.CTkToplevel()
        self.pop_out = pop_out
        w = 700
        h = 300
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)

        with open('prompts.json', 'r') as file:
            prompts = json.load(file)

        label = ctk.CTkLabel(
            text=prompts['dir_not_found'], master=pop_out,
            font=('Helvetica bold', 26))

        label.grid(row=0, column=0, sticky='nsew', columnspan=2)

        self.image_directory = ctk.StringVar()
        self.image_directory.set(str(Path("Images").resolve()))
        self.image_directory.trace(
            "w", lambda name, index, mode,
            image_directory=self.
            image_directory: self.image_directory_callback(image_directory))

        directory_entry = ctk.CTkEntry(
            master=pop_out, textvariable=self.image_directory,
            placeholder_text="select the directory which contains the files",
            width=500, height=40, font=('Helvetica bold', 16),
            state=ctk.DISABLED)

        directory_entry.bind(
            "<Button-1>", command=lambda event, pop_out=pop_out,
            image_directory=self.image_directory: self.select_directory(
                event, pop_out, image_directory))

        directory_entry.grid(row=1, column=0, columnspan=2)

        self.submit_button = ctk.CTkButton(
            text="Submit", state=ctk.DISABLED, command=self.submit, width=w //
            2 - 20, height=h // 5, master=pop_out, font=('Helvetica bold', 30))
        self.submit_button.grid(row=2, column=0, sticky='sew',
                                pady=(0, 10), padx=(10, 5))
        menu_button = ctk.CTkButton(
            text="Return to menu", command=lambda: self.back_to_menu(False),
            width=w // 2 - 20, height=h // 5, master=pop_out,
            font=('Helvetica bold', 30))
        menu_button.grid(row=2, column=1, sticky='sew',
                         pady=(0, 10), padx=(5, 10))

        pop_out.protocol("WM_DELETE_WINDOW", self.on_closing)

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)

    def image_directory_callback(self, image_directory: ctk.StringVar):
        """
        Callback function for the image directory variable.

        Args:
            image_directory (StringVar): The image directory.
        """
        if all([os.path.isfile(image_directory.get() + "/" + k)
                for k in self.save_obj["sort_alg"].data]):
            self.submit_button.configure(state=ctk.NORMAL)

    def select_directory(self, event, root: ctk.CTk,
                         directory_var: ctk.StringVar):
        """
        Selects a directory using a file dialog.

        Args:
            event: The event that triggered the callback.
            root (CTk): The root Tk object.
            directory_var (StringVar): The directory.
        """
        directory = ctk.filedialog.askdirectory(parent=root)
        directory_var.set(directory)

    def submit(self):
        """Submits the selected image directory path."""
        self.submit_path(self.image_directory.get())
        self.pop_out.destroy()

    def on_closing(self):
        """Event handler for the pop-out window closing."""
        self.back_to_menu(False)
