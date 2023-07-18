import json
import pickle
from pathlib import Path
from typing import Callable, List

import customtkinter as ctk

from creation_pop_out import CreationPopOut
from utils import add_hover, get_full_path


class MenuScreen():
    """
    Represents the menu screen of the Rank-Based Annotation application.
    """

    def __init__(self, root: ctk.CTk, creation_callback: Callable,
                 ordering_callback: Callable, center: Callable,
                 open_user_selection: Callable, advanced_settings_callback: Callable):
        """
        Initializes the MenuScreen instance.

        Args:
            root (CTk): The root window of the application.
            creation_callback (function): The callback function for creating a 
                                          new annotation.
            ordering_callback (function): The callback function for loading a 
                                          saved annotation.
            center (function): The function to center the window.
            open_user_selection (function): The function to open user selection.
            advanced_settings_callback (function): Calback function to bring up the
            advanced settings menu.
        """

        self.root = root

        self.creation_callback = creation_callback
        self.ordering_callback = ordering_callback
        self.advanced_settings_callback = advanced_settings_callback
        self.center = center
        self.open_user_selection = open_user_selection

        with open('prompts.json', 'r') as file:
            prompts = json.load(file)

        path = get_full_path("saves")

        self.paths = list(Path(path).glob('*.pickle'))

        self.saves = [pickle.load(open(path, 'rb')) for path in self.paths]

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation",
            font=('Helvetica bold', 40))

        self.menu_frame = ctk.CTkFrame(master=self.root)

        self.instructions_frame = ctk.CTkFrame(master=self.root)

        self.new_button = ctk.CTkButton(
            master=self.menu_frame, text="New Annotation", width=250,
            height=45, font=('Helvetica bold', 20),
            command=self.new_annotation)
        self.delete_button = ctk.CTkButton(
            master=self.menu_frame, text="Delete Annotation", width=250,
            height=45, font=('Helvetica bold', 20))

        self.saved_annotations_header = ctk.CTkFrame(
            master=self.menu_frame, corner_radius=0,
            fg_color=self.menu_frame.cget("fg_color"))

        self.saved_annotations_header.grid_columnconfigure(
            0, weight=1, uniform="header")
        self.saved_annotations_header.grid_columnconfigure(
            1, weight=1, uniform="header")
        self.saved_annotations_header.grid_columnconfigure(
            2, weight=1, uniform="header")
        self.saved_annotations_header.grid_columnconfigure(
            3, weight=1, uniform="header")
        self.saved_annotations_header.grid_rowconfigure(
            0, weight=1, uniform="header")

        self.header_name_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Name:",
            font=('Helvetica bold', 20))

        self.user_label = ctk.CTkLabel(
            master=self.root, text="", font=('Helvetica bold', 24))

        self.user_label.bind("<Enter>", lambda event, og_color=self.user_label.cget(
            'text_color'): self.highlight_label(self.user_label, og_color))
        self.user_label.bind("<Leave>", lambda event, og_color=self.user_label.cget(
            'text_color'): self.remove_highlight_label(self.user_label, og_color))
        self.user_label.bind(
            "<Button-1>", lambda event: self.open_user_selection())

        self.header_algorithm_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Algorithm:",
            font=('Helvetica bold', 20))

        self.header_images_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Images:",
            font=('Helvetica bold', 20))

        self.header_count_label = ctk.CTkLabel(
            master=self.saved_annotations_header,
            text="Total annotations made:", font=('Helvetica bold', 20))

        self.saved_annotations_frame = ctk.CTkScrollableFrame(
            master=self.menu_frame, height=400)

        self.saved_annotations_frame.columnconfigure(0, weight=1)

        self.text_header = ctk.CTkLabel(
            master=self.instructions_frame,
            text="Welcome to the Rank-Based Annotation program",
            font=('Helvetica bold', 24),
            wraplength=400)

        self.text = ctk.CTkLabel(
            master=self.instructions_frame,
            text=prompts['instruction_prompt'],
            font=('Helvetica bold', 18),
            wraplength=400, anchor="w", justify=ctk.LEFT)

        self.text.bind(
            '<Configure>', lambda event: self.update_wraplength(self.text))
        self.old_size = self.text.winfo_width()

    def display(self):
        """Displays the menu screen."""

        self.root.grid_rowconfigure(0, weight=1, uniform="header")
        self.root.grid_rowconfigure(1, weight=8, uniform="header")
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.header.grid(row=0, column=0, columnspan=2, sticky="S")
        self.user_label.place(relx=0.98, rely=0.02, anchor='ne')
        self.menu_frame.grid(row=1, column=0, sticky="nsew",
                             padx=(20, 10), pady=20)

        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.menu_frame.grid_rowconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(1, weight=3)
        self.menu_frame.grid_rowconfigure(2, weight=1)

        self.instructions_frame.grid(
            row=1, column=1, sticky="nsew", padx=(20, 10), pady=20)

        self.instructions_frame.grid_columnconfigure(0, weight=1)
        self.instructions_frame.grid_rowconfigure(0, weight=1)
        self.instructions_frame.grid_rowconfigure(1, weight=5)

        self.new_button.grid(row=2, column=0, columnspan=2, padx=(
            20, 10), pady=10)

        self.saved_annotations_header.grid(
            row=0, column=0, columnspan=2, sticky="sew", padx=(10, 20),
            pady=(20, 0))

        self.header_name_label.grid(
            row=0, column=0, sticky="w", padx=10, pady=4)
        self.header_algorithm_label.grid(
            row=0, column=1, sticky="w", padx=10, pady=4)
        self.header_images_label.grid(
            row=0, column=2, sticky="w", padx=10, pady=4)
        self.header_count_label.grid(
            row=0, column=3, sticky="w", padx=10, pady=4)

        self.saved_annotations_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 0))

        self.display_saves()

        self.text_header.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self.text.grid(row=1, column=0, padx=20, pady=10, sticky="new")

    def display_user(self, user: str):
        """
        Displays the user label with the provided username.

        Args:
            user (str): The username to display.
        """
        self.user_label.configure(text=user)

    def display_saves(self):
        """
        Displays the saved annotations in the menu.
        """

        for i, save in enumerate(self.saves):
            self.append_row(i, save)

    def append_row(self, index: int, save: dict):
        """
        Appends a row with save information to the saved annotations frame.

        Args:
            index (int): The index of the save.
            save (dict): The save object.
        """

        saved_annotations_row = ctk.CTkFrame(
            master=self.saved_annotations_frame)

        saved_annotations_row.bind(
            "<Button-1>", command=lambda event, i=index: self.load_save(i))

        saved_annotations_row.grid(row=index, column=0, sticky="ew", pady=3)

        saved_annotations_row.grid_columnconfigure(0, weight=1, uniform="row")
        saved_annotations_row.grid_columnconfigure(1, weight=1, uniform="row")
        saved_annotations_row.grid_columnconfigure(2, weight=1, uniform="row")
        saved_annotations_row.grid_columnconfigure(3, weight=1, uniform="row")
        saved_annotations_row.grid_rowconfigure(0, weight=1, uniform="row")

        save_name_label = ctk.CTkLabel(
            master=saved_annotations_row, text=save["name"],
            font=('Helvetica bold', 20))
        save_name_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        sort_alg = save["sort_alg"]

        algorithm_label = ctk.CTkLabel(
            master=saved_annotations_row, text=type(sort_alg).__name__,
            font=('Helvetica bold', 20))

        algorithm_label.grid(row=0, column=1, padx=10, pady=4, sticky="w")

        total_images = len(sort_alg.data)

        total_images_label = ctk.CTkLabel(
            master=saved_annotations_row, text=total_images,
            font=('Helvetica bold', 20))

        total_images_label.grid(row=0, column=2, padx=10, pady=4, sticky="w")

        comp_count = sort_alg.get_comparison_count()

        count_label = ctk.CTkLabel(
            master=saved_annotations_row, text=comp_count,
            font=('Helvetica bold', 20))

        count_label.grid(row=0, column=3, padx=10, pady=4, sticky="w")

        for child in saved_annotations_row.winfo_children():
            child.bind("<Button-1>", command=lambda event,
                       i=index: self.load_save(i))

        add_hover(saved_annotations_row)

    def new_annotation(self):
        """
        Callback function for the new annotation button.
        """

        CreationPopOut(self.creation_callback, self.center, 
                       self.advanced_settings_callback)

    def load_save(self, index):
        """
        Loads the save object associated with the index

        Args:
            index (int): The index of the save.

        """
        file = open(self.paths[index], 'rb')
        save_obj = pickle.load(file)
        self.ordering_callback(save_obj)

    def update_wraplength(self, label: ctk.CTkLabel):
        """
        Updates the wraplength of the label based on its width.

        Args:
            label (CTkLabel): The label to update.
        """

        if abs(label.winfo_width() - self.old_size) > 20:
            self.old_size = label.winfo_width()
            label.configure(wraplength=label.winfo_width() - 10)

    def highlight_label(self, label: ctk.CTkLabel, og_color: List[str]):
        """
        Highlights the label on mouse hover.

        Args:
            label (ctk.CTkLabel): The label to be highlighted.
            og_color (List[str]): The original color of the label as a list of 
                                  strings representing the color code.
        """
        gray_color = int(og_color[1][-2:]) + 10

        if gray_color > 100:
            gray_color = 100

        label.configure(text_color='gray' + str((gray_color)))

    def remove_highlight_label(self, label: ctk.CTkLabel, og_color: List[str]):
        """
        Removes the highlight from the specified label by restoring its original
        text color.

        Args:
            label (ctk.CTkLabel): The label from which to remove the highlight.
            og_color (List[str]): The original color of the label as a list of 
                                  strings representing the color code.
        """
        label.configure(text_color=og_color)
