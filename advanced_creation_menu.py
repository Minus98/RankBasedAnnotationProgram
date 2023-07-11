
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image


class AdvancedCreationMenu():

    def __init__(
            self, root: ctk.CTk, creation_callback: Callable,
            menu_callback: Callable):

        self.root = root

        self.rating_buttons = [("Rating 1", 1), ("Rating 2", 2)]

        self.basic_settings_frame = ctk.CTkFrame(self.root)

        self.advanced_settings_frame = ctk.CTkFrame(self.root)

        # Basic settings

        self.name_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Name:",
            font=('Helvetica bold', 20))

        self.name = ctk.StringVar()

        self.name_entry = ctk.CTkEntry(
            master=self.basic_settings_frame, textvariable=self.name,
            placeholder_text="Enter the name of the annotation session",
            width=200, height=40, font=('Helvetica bold', 20))

        self.algorithm_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Algorithm:",
            font=('Helvetica bold', 20))

        self.comp_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Comparison Size:",
            font=('Helvetica bold', 20))

        self.slider_frame = ctk.CTkFrame(
            master=self.basic_settings_frame,
            fg_color=self.basic_settings_frame.cget("fg_color"))

        self.comparison_size_label = ctk.CTkLabel(
            master=self.slider_frame, font=('Helvetica bold', 25))

        self.slider = ctk.CTkSlider(
            master=self.slider_frame, from_=2, to=4, number_of_steps=2,
            command=lambda val,
            label=self.comparison_size_label: self.update_comparison_size(
                val, label))

        self.slider.set(2)

        self.comparison_size_label.configure(text=int(self.slider.get()))

        self.algorithm_selection = ctk.CTkOptionMenu(
            master=self.basic_settings_frame,
            values=["True Skill", "Merge Sort", "Rating", "Hybrid"],
            width=200, height=40, font=('Helvetica bold', 20),
            command=lambda value, parent=self.basic_settings_frame,
            slider=self.slider, slider_frame=self.slider_frame,
            label=self.comparison_size_label,
            comp_label=self.comp_label: self.algorithm_changed(
                value, parent, slider, slider_frame, label, comp_label))

        self.image_dir_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Image Directory:",
            font=('Helvetica bold', 20))

        self.image_directory = ctk.StringVar()
        self.image_directory.set(str(Path("data/Images").resolve()))

        self.directory_entry = ctk.CTkEntry(
            master=self.basic_settings_frame, textvariable=self.image_directory,
            placeholder_text="select the directory which contains the files",
            width=400, height=40, font=('Helvetica bold', 16),
            state=ctk.DISABLED)

        self.directory_entry.bind(
            "<Button-1>", command=lambda event,
            parent=self.basic_settings_frame,
            image_directory=self.image_directory: self.select_directory(
                parent, image_directory))

        self.enable_scrolling_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Enable Scrolling:",
            font=('Helvetica bold', 20))

        self.scroll_enabled = ctk.BooleanVar()
        self.scroll_enabled_checkbox = ctk.CTkCheckBox(
            master=self.basic_settings_frame, variable=self.scroll_enabled,
            text="", checkbox_width=30, checkbox_height=30, onvalue=True,
            offvalue=False)

        # Advanced settings

        self.prompt_label = ctk.CTkLabel(
            master=self.advanced_settings_frame, text="Annotation prompt:",
            font=('Helvetica bold', 20))

        self.prompt = ctk.StringVar()

        self.prompt_entry = ctk.CTkEntry(
            master=self.advanced_settings_frame, textvariable=self.prompt,
            placeholder_text="Enter the text prompt for annotations",
            width=300, height=40, font=('Helvetica bold', 16))

        self.ratings_list_label = ctk.CTkLabel(
            master=self.advanced_settings_frame, text="Rating Options",
            font=('Helvetica bold', 20))

        self.ratings_list = ctk.CTkScrollableFrame(
            master=self.advanced_settings_frame, height=120)

        self.create_button = ctk.CTkButton(
            master=self.root, text="Create Annotation", width=200, height=40,
            font=('Helvetica bold', 20),
            command=lambda name=self.name,
            algorithm_selection=self.algorithm_selection, slider=self.slider,
            image_directory=self.image_directory,
            scroll_enabled=self.scroll_enabled: self.create_save(
                name, algorithm_selection, slider, image_directory,
                scroll_enabled))

        self.cancel_button = ctk.CTkButton(
            master=self.root, text="Cancel", width=200, height=40,
            font=('Helvetica bold', 20),
            command=menu_callback)

    def display(self):

        self.basic_settings_frame.grid_rowconfigure(
            0, weight=2, uniform="ordering")
        self.basic_settings_frame.grid_rowconfigure(
            1, weight=2, uniform="ordering")
        self.basic_settings_frame.grid_rowconfigure(
            2, weight=1, uniform="ordering")
        self.basic_settings_frame.grid_rowconfigure(
            3, weight=2, uniform="ordering")
        self.basic_settings_frame.grid_columnconfigure(0, weight=1)
        self.basic_settings_frame.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=1, uniform="header")
        self.root.grid_rowconfigure(1, weight=8, uniform="header")
        self.root.grid_rowconfigure(2, weight=1, uniform="header")

        self.name_label.grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        self.name_entry.grid(row=0, column=1, padx=10,
                             pady=(10, 2), sticky="w")

        self.algorithm_label.grid(row=1, column=0, padx=10, pady=2, sticky="e")

        self.comp_label.grid(
            row=2, column=0, padx=10, pady=2, sticky="e")

        self.slider_frame.grid(
            row=2, column=1, padx=10, pady=2, sticky="w")

        self.slider.grid(row=0, column=0)

        self.comparison_size_label.grid(row=0, column=1, padx=5)

        self.algorithm_selection.grid(
            row=1, column=1, padx=10, pady=2, sticky="w")

        self.image_dir_label.grid(
            row=3, column=0, padx=10, pady=(2, 10),
            sticky="e")

        self.directory_entry.grid(row=3, column=1, padx=10,
                                  pady=(2, 10), sticky="w")

        self.enable_scrolling_label.grid(
            row=4, column=0, padx=10, pady=2, sticky="e")

        self.scroll_enabled_checkbox.grid(
            row=4, column=1, padx=10, pady=2, sticky="w")

        self.root.grid_columnconfigure(
            0, weight=1, uniform="advanced_settings")
        self.root.grid_columnconfigure(
            1, weight=1, uniform="advanced_settings")

        self.basic_settings_frame.grid(
            row=1, column=0, padx=(20, 10), pady=20, sticky="nesw")

        """self.advanced_settings_frame.grid_rowconfigure(
            0, weight=2, uniform="advanced_frame")
        self.advanced_settings_framee.grid_rowconfigure(
            1, weight=2, uniform="advanced_frame")
        self.advanced_settings_frame.grid_rowconfigure(
            2, weight=1, uniform="advanced_frame")
        self.advanced_settings_frame.grid_rowconfigure(
            3, weight=2, uniform="advanced_frame")"""
        self.advanced_settings_frame.grid_columnconfigure(0, weight=1)
        self.advanced_settings_frame.grid_columnconfigure(1, weight=1)

        self.prompt_label.grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        self.prompt_entry.grid(row=0, column=1, padx=10,
                               pady=(10, 2), sticky="w")

        self.ratings_list_label.grid(row=1, column=0, columnspan=2)

        self.ratings_list.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.ratings_list.grid_columnconfigure(0, weight=1)

        self.advanced_settings_frame.grid(
            row=1, column=1, padx=(10, 20), pady=20, sticky="nesw")

        # Buttons

        self.cancel_button.grid(row=2, column=0)
        self.create_button.grid(row=2, column=1)

        self.refresh_rating_buttons()

    def algorithm_changed(
            self, value: str, parent: ctk.CTkToplevel, slider: ctk.CTkSlider,
            slider_frame: ctk.CTkFrame, label: ctk.CTkLabel,
            comp_label: ctk.CTkLabel):
        """
        Handles the change event of the algorithm selection option menu.

        Args:
            value (str): The selected algorithm.
            pop_out (CTkToplevel): The pop-out window.
            slider (CTkSlider): The slider widget.
            slider_frame (CTkFrame): The frame containing the slider.
            label (CTkLabel): The label displaying the comparison size.
            comp_label (CTkLabel): The label for comparison size.
        """

        if value == "Merge Sort":
            self.change_slider_row_state(
                True, parent, slider_frame, comp_label)
            slider.set(2)
            label.configure(text=2, state=ctk.DISABLED)
            comp_label.configure(state=ctk.DISABLED)
            slider.configure(state=ctk.DISABLED)

        elif value == "Rating":
            self.change_slider_row_state(
                False, parent, slider_frame, comp_label)

        else:
            self.change_slider_row_state(
                True, parent, slider_frame, comp_label)
            slider.configure(state=ctk.NORMAL)
            label.configure(state=ctk.NORMAL)
            comp_label.configure(state=ctk.NORMAL)

    def change_slider_row_state(
            self, state: bool, parent: ctk.CTkToplevel,
            slider_frame: ctk.CTkFrame, comp_label: ctk.CTkLabel):
        """
        Changes the state of the slider row.

        Args:
            state (bool): Boolean indicating whether the slider row should be 
            enabled or disabled.
            pop_out (CTkToplevel): The pop-out window.
            slider_frame (CTkFrame): The frame containing the slider.
            comp_label (CTkLabel): The label for comparison size.
        """
        if state:
            comp_label.grid()
            slider_frame.grid()
            parent.rowconfigure(index=2, weight=1)

        else:
            comp_label.grid_remove()
            slider_frame.grid_remove()
            parent.rowconfigure(index=2, weight=0)

    def update_comparison_size(self, val: int, label: ctk.CTkLabel):
        """
        Updates the comparison size label based on the slider value.

        Args:
            value (int): The current slider value.
            label (CTkLabel): The label to be updated.
        """
        label.configure(text=int(val))

    def select_directory(self, root: ctk.CTkToplevel,
                         directory_var: ctk.StringVar):
        """
        Callback function to select a directory using a file dialog.

        Args:
            root (CTkToplevel): The root window or parent widget.
            directory_var (StringVar): The element to store the selected 
            directory.
        """
        directory = ctk.filedialog.askdirectory(parent=root)
        directory_var.set(directory)

    def refresh_rating_buttons(self):

        for child in self.ratings_list.winfo_children():
            child.destroy()

        for index, button in enumerate(self.rating_buttons):
            self.append_row(index, button)

    def append_row(self, index, button):

        row = ctk.CTkFrame(self.ratings_list)

        button_text = ctk.CTkLabel(
            row, text="Text: " + button[0],
            font=('Helvetica bold', 20))
        button_value = ctk.CTkLabel(
            row, text="Value: " + str(index),
            font=('Helvetica bold', 20))

        button_up_state = ctk.NORMAL
        button_down_state = ctk.NORMAL

        if index <= 0:
            button_up_state = ctk.DISABLED

        if index >= len(self.rating_buttons) - 1:
            button_down_state = ctk.DISABLED

        button_up = ctk.CTkButton(
            row, text="▲", state=button_up_state, width=28,
            command=lambda i=index: self.move_up(i))
        button_down = ctk.CTkButton(
            row, text="▼", state=button_down_state, width=28,
            command=lambda i=index: self.move_down(i))
        delete_button = ctk.CTkButton(
            row, text="X", width=28, command=lambda i=index: self.delete_rating(i))

        row.grid(row=index, column=0, sticky="ew", pady=3)

        row.grid_columnconfigure(0, weight=2, uniform="row")
        row.grid_columnconfigure(1, weight=2, uniform="row")
        row.grid_columnconfigure(2, weight=1, uniform="row")
        row.grid_columnconfigure(3, weight=1, uniform="row")
        row.grid_columnconfigure(4, weight=1, uniform="row")

        button_value.grid(row=0, column=0, sticky="w", padx=5, pady=3)
        button_text.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        button_up.grid(row=0, column=2, sticky="e", padx=5, pady=3)
        button_down.grid(row=0, column=3, sticky="e", padx=5, pady=3)
        delete_button.grid(row=0, column=4, sticky="e", padx=5, pady=3)

    def delete_rating(self, index: int):

        del (self.rating_buttons[index])
        self.refresh_rating_buttons()

    def move_up(self, index: int):

        if index > 0:
            temp = self.rating_buttons[index]
            self.rating_buttons[index] = self.rating_buttons[index - 1]
            self.rating_buttons[index - 1] = temp

        self.refresh_rating_buttons()

    def move_down(self, index: int):

        if index < len(self.rating_buttons) - 1:
            temp = self.rating_buttons[index]
            self.rating_buttons[index] = self.rating_buttons[index + 1]
            self.rating_buttons[index + 1] = temp

        self.refresh_rating_buttons()
