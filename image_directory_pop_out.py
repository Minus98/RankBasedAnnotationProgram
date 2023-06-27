import json
import os
from pathlib import Path

import customtkinter as ctk


class ImageDirectoryPopOut():

    def __init__(self, root, center, save_obj, submit_path, back_to_menu):

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

    def image_directory_callback(self, image_directory):
        if all([os.path.isfile(image_directory.get() + "/" + k)
                for k in self.save_obj["sort_alg"].data]):
            self.submit_button.configure(state=ctk.NORMAL)

    def select_directory(self, event, root, directory_var):
        directory = ctk.filedialog.askdirectory(parent=root)
        directory_var.set(directory)

    def submit(self):
        self.submit_path(self.image_directory.get())
        self.pop_out.destroy()

    def on_closing(self):
        self.back_to_menu(False)
