
import os
import pickle
import random
import sys
import time
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
import pandas as pd

import sorting_algorithms as sa
import utils


class AdvancedCreationMenu():
    """
    Class representing the more advanced creation menu which allows the user to 
    customize ranking and rating buttons and prompts and more.
    """

    def __init__(
            self, root: ctk.CTk, menu_callback: Callable,
            initial_settings: Optional[dict] = None):
        """
        Initializes the AdvancedCreationMenu instance.

        Args:
            root (CTk): The root cutom tkinter object.
            menu_callback (function): Callback function to return to the main menu.

        """

        self.root = root

        self.rating_buttons = ["Rating 1", "Rating 2"]

        self.ranking_buttons = [ctk.StringVar(value="") for _ in range(5)]

        self.basic_settings_frame = ctk.CTkFrame(self.root)
        self.menu_callback = menu_callback
        self.advanced_settings_frame = ctk.CTkFrame(self.root)

        # General settings

        self.basic_settings_pady = 15

        self.general_settings_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="General Settings",
            font=('Helvetica bold', 24))

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

        self.algorithm_selection = ctk.CTkOptionMenu(
            master=self.basic_settings_frame,
            values=["True Skill", "Merge Sort", "Rating", "Hybrid"],
            width=200, height=40, font=('Helvetica bold', 20),
            command=lambda value: self.algorithm_changed())

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

        self.comparison_count_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Max Total Comparisons:",
            font=('Helvetica bold', 20)
        )

        vcmd = (self.root.register(self.validate), '%P')

        self.comparison_count_entry = ctk.CTkEntry(
            master=self.basic_settings_frame, validate='key',
            validatecommand=vcmd, width=200, height=40,
            font=('Helvetica bold', 20))

        self.user_comparison_count_label = ctk.CTkLabel(
            master=self.basic_settings_frame, text="Max User Comparisons:",
            font=('Helvetica bold', 20)
        )

        self.user_comparison_count_entry = ctk.CTkEntry(
            master=self.basic_settings_frame, validate='key',
            validatecommand=vcmd, width=200, height=40,
            font=('Helvetica bold', 20))

        # Advanced settings

        self.rating_list_frame = ctk.CTkFrame(
            self.advanced_settings_frame,
            fg_color=self.advanced_settings_frame.cget("fg_color"))

        self.rating_prompt_label = ctk.CTkLabel(
            master=self.rating_list_frame, text="Rating prompt:",
            font=('Helvetica bold', 20))

        self.rating_prompt = ctk.StringVar()

        self.rating_prompt_entry = ctk.CTkEntry(
            master=self.rating_list_frame, textvariable=self.rating_prompt,
            placeholder_text="Enter the text prompt for annotations",
            width=300, height=40, font=('Helvetica bold', 16))

        self.ratings_list_label = ctk.CTkLabel(
            master=self.rating_list_frame, text="Rating Options",
            font=('Helvetica bold', 24))

        self.ratings_list = ctk.CTkScrollableFrame(
            master=self.rating_list_frame, height=120)

        self.edit_index = -1

        self.ranking_list_frame = ctk.CTkFrame(
            self.advanced_settings_frame,
            fg_color=self.advanced_settings_frame.cget("fg_color"))

        self.ranking_list_label = ctk.CTkLabel(
            master=self.ranking_list_frame, text="Ranking Options",
            font=('Helvetica bold', 24))

        self.ranking_list = ctk.CTkFrame(
            master=self.ranking_list_frame, height=120)

        self.ranking_prompt_label = ctk.CTkLabel(
            master=self.ranking_list_frame, text="Ranking prompt:",
            font=('Helvetica bold', 20))

        self.ranking_prompt = ctk.StringVar()

        self.ranking_prompt_entry = ctk.CTkEntry(
            master=self.ranking_list_frame, textvariable=self.ranking_prompt,
            placeholder_text="Enter the text prompt for annotations",
            width=300, height=40, font=('Helvetica bold', 16))

        self.switch_frame = ctk.CTkFrame(self.ranking_list_frame)

        self.ranking_equals_switch = ctk.CTkSwitch(
            self.switch_frame, text="=", font=('Helvetica bold', 18), width=70,
            command=self.refresh_ranking_buttons)

        self.ranking_much_greater_switch = ctk.CTkSwitch(
            self.switch_frame, text=">>", font=('Helvetica bold', 18),
            width=70, command=self.refresh_ranking_buttons)

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

        if initial_settings:
            self.set_initial_settings(initial_settings)

        self.comparison_size_label.configure(text=int(self.slider.get()))

    def set_initial_settings(self, initial_settings: dict):
        """
        Updates the values of the relevant fields with the initial settings provided.

        Args:
            initial_settings (dict): The dictionary containing the fields and their
                                     corresponding initial values.
        """

        if 'name' in initial_settings:
            self.name.set(initial_settings['name'])

        if 'algorithm_selection' in initial_settings:
            self.algorithm_selection.set(
                initial_settings['algorithm_selection'])

        if 'image_directory' in initial_settings:
            self.image_directory.set(initial_settings['image_directory'])

        if 'slider' in initial_settings:
            self.slider.set(initial_settings['slider'])

        if 'scroll_enabled' in initial_settings:
            self.scroll_enabled.set(initial_settings['scroll_enabled'])

        self.algorithm_changed()

    def display(self):
        """
        Displays the content of the advanced creation menu view.
        """

        self.basic_settings_frame.grid_columnconfigure(0, weight=1)
        self.basic_settings_frame.grid_columnconfigure(1, weight=1)

        self.root.grid_rowconfigure(0, weight=1, uniform="header")
        self.root.grid_rowconfigure(1, weight=16, uniform="header")
        self.root.grid_rowconfigure(2, weight=2, uniform="header")

        self.general_settings_label.grid(
            row=0, column=0, columnspan=2, padx=10, pady=10)

        self.name_label.grid(row=1, column=0, padx=10,
                             pady=self.basic_settings_pady, sticky="e")

        self.name_entry.grid(row=1, column=1, padx=10,
                             pady=self.basic_settings_pady, sticky="w")

        self.algorithm_label.grid(
            row=2, column=0, padx=10, pady=self.basic_settings_pady,
            sticky="e")

        if self.should_show_ranking_options():
            self.comp_label.grid(row=3, column=0, padx=10,
                                 pady=self.basic_settings_pady, sticky="e")

            self.slider_frame.grid(
                row=3, column=1, padx=10, pady=self.basic_settings_pady,
                sticky="w")

            self.comparison_count_label.grid(
                row=6, column=0, padx=10, pady=self.basic_settings_pady,
                sticky="e")

            self.comparison_count_entry.grid(
                row=6, column=1, padx=10, pady=self.basic_settings_pady,
                sticky="w")

        self.slider.grid(row=0, column=0)

        self.comparison_size_label.grid(row=0, column=1, padx=5)

        self.algorithm_selection.grid(
            row=2, column=1, padx=10, pady=self.basic_settings_pady,
            sticky="w")

        self.image_dir_label.grid(
            row=4, column=0, padx=10, pady=self.basic_settings_pady,
            sticky="e")

        self.directory_entry.grid(row=4, column=1, padx=10,
                                  pady=self.basic_settings_pady, sticky="w")

        self.enable_scrolling_label.grid(
            row=5, column=0, padx=10, pady=self.basic_settings_pady,
            sticky="e")

        self.scroll_enabled_checkbox.grid(
            row=5, column=1, padx=10, pady=self.basic_settings_pady,
            sticky="w")

        """
        self.user_comparison_count_label.grid(
            row=7, column=0, padx=10, pady=self.basic_settings_pady, sticky="e"
        )

        self.user_comparison_count_entry.grid(
            row=7, column=1, padx=10, pady=self.basic_settings_pady, sticky="w"
        )"""

        self.root.grid_columnconfigure(
            0, weight=1, uniform="advanced_settings")
        self.root.grid_columnconfigure(
            1, weight=1, uniform="advanced_settings")

        self.basic_settings_frame.grid(
            row=1, column=0, padx=(20, 10), pady=20, sticky="nesw")

        self.advanced_settings_frame.grid_columnconfigure(0, weight=1)
        self.advanced_settings_frame.grid_columnconfigure(1, weight=1)

        self.advanced_settings_frame.grid(
            row=1, column=1, padx=(10, 20), pady=20, sticky="nesw")

        # Buttons

        self.cancel_button.grid(row=2, column=0)
        self.create_button.grid(row=2, column=1)

        self.ratings_list_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.rating_prompt_label.grid(
            row=1, column=0, padx=10, pady=10, sticky="e")

        self.rating_prompt_entry.grid(row=1, column=1, padx=10,
                                      pady=10, sticky="w")

        self.ratings_list.grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.ratings_list.grid_columnconfigure(0, weight=1)
        self.rating_list_frame.grid_columnconfigure(0, weight=1)
        self.rating_list_frame.grid_columnconfigure(1, weight=1)

        self.ranking_list_frame.grid_columnconfigure(0, weight=1)
        self.ranking_list_frame.grid_columnconfigure(1, weight=1)
        self.ranking_list.grid_columnconfigure(0, weight=1)
        self.ranking_list.grid_columnconfigure(1, weight=1)

        self.ranking_list_label.grid(row=0, column=0, columnspan=2, pady=10)

        self.ranking_prompt_label.grid(
            row=1, column=0, padx=10, pady=10, sticky="e")

        self.ranking_prompt_entry.grid(row=1, column=1, padx=10,
                                       pady=10, sticky="w")

        self.switch_frame.grid(
            row=2, column=1, sticky="e", padx=10, pady=(10, 0))

        self.switch_frame.columnconfigure(0, weight=1)
        self.switch_frame.columnconfigure(1, weight=1)

        self.ranking_equals_switch.grid(
            row=0, column=0, sticky="e", padx=(10, 5), pady=5)
        self.ranking_much_greater_switch.grid(
            row=0, column=1, sticky="e", padx=(5, 10), pady=5)

        self.ranking_list.grid(
            row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))

        if self.should_show_rating_options():
            self.show_rating_options()

        if self.should_show_ranking_options():
            self.show_ranking_options()

    def show_ranking_options(self):
        """
        Displays the ranking options frame.
        """

        self.ranking_list_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew")

        self.refresh_ranking_buttons()

    def show_rating_options(self):
        """
        Displays the rating options frame.
        """

        self.rating_list_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew")

        self.refresh_rating_buttons()

    def show_comparison_count(self):
        """
        Displays the comparison count label and entry in the basic settings frame.
        """

        self.comparison_count_label.grid(
            row=6, column=0, padx=10, pady=self.basic_settings_pady,
            sticky="e")

        self.comparison_count_entry.grid(
            row=6, column=1, padx=10, pady=self.basic_settings_pady,
            sticky="w")

    def hide_rating_options(self):
        """
        Hides the rating options frame.
        """

        self.rating_list_frame.grid_remove()

    def hide_ranking_options(self):
        """
        Hides the ranking options frame.
        """

        self.ranking_list_frame.grid_remove()

    def hide_comparison_count(self):
        """
        Hides the comparison count label and entry.
        """

        self.comparison_count_label.grid_remove()
        self.comparison_count_entry.grid_remove()

    def refresh_ranking_buttons(self):
        """
        Updates to ranking options frame so that the correct fields are displayed.
        """

        for child in self.ranking_list.winfo_children():
            child.destroy()

        current_row = 0

        if not self.should_show_switches():

            self.ranking_equals_switch.deselect()
            self.ranking_equals_switch.configure(state=ctk.DISABLED)

            self.ranking_much_greater_switch.deselect()
            self.ranking_much_greater_switch.configure(state=ctk.DISABLED)
        else:

            self.ranking_equals_switch.configure(state=ctk.NORMAL)
            self.ranking_much_greater_switch.configure(state=ctk.NORMAL)

        if self.ranking_equals_switch.get():

            equals_frame = ctk.CTkFrame(
                master=self.ranking_list, fg_color=self.ranking_list.cget(
                    "fg_color"))

            self.populate_rank_entry_frame(equals_frame, "A == B:", 2)

            equals_frame.grid(row=current_row, column=0, pady=5, columnspan=2)

            current_row += 1

        # A > B

        A_greater_frame = ctk.CTkFrame(
            master=self.ranking_list, fg_color=self.ranking_list.cget(
                "fg_color"))

        self.populate_rank_entry_frame(A_greater_frame, "A > B:", 1)

        A_greater_frame.grid(row=current_row, column=0, pady=5)

        # A < B

        B_greater_frame = ctk.CTkFrame(
            master=self.ranking_list, fg_color=self.ranking_list.cget(
                "fg_color"))

        self.populate_rank_entry_frame(B_greater_frame, "A < B:", 3)

        B_greater_frame.grid(row=current_row, column=1, pady=5)

        current_row += 1

        if self.ranking_much_greater_switch.get():

            # A >> B

            A_much_greater_frame = ctk.CTkFrame(
                master=self.ranking_list, fg_color=self.ranking_list.cget(
                    "fg_color"))

            self.populate_rank_entry_frame(A_much_greater_frame, "A >> B:", 0)

            A_much_greater_frame.grid(row=current_row, column=0, pady=5)

            # A << B

            B_much_greater_frame = ctk.CTkFrame(
                master=self.ranking_list, fg_color=self.ranking_list.cget(
                    "fg_color"))

            self.populate_rank_entry_frame(B_much_greater_frame, "A << B:", 4)

            B_much_greater_frame.grid(row=current_row, column=1, pady=5)

            current_row += 1

    def populate_rank_entry_frame(
            self, frame: ctk.CTkFrame, text: str, var_index: int):
        """
        Adds the widgets associated with each of the rank entries.

        Args:
            frame (CTkFrame): The frame that is to be populated.
            text (str): The label text of the specific entry.
            var_index: The index of the text variable in the ranking_buttons list that
                       should be associated with this specific entry.
        """
        label = ctk.CTkLabel(
            master=frame, text=text,
            font=('Helvetica bold', 18), width=60, anchor="e")

        entry = ctk.CTkEntry(master=frame, width=200,
                             font=('Helvetica bold', 16),
                             textvariable=self.ranking_buttons[var_index])

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        label.grid(row=0, column=0, sticky="e", pady=5, padx=5)
        entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

    def algorithm_changed(
            self):
        """
        Handles the change event of the algorithm selection option menu.
        """

        value = self.algorithm_selection.get()
        if value == "Merge Sort":
            self.change_slider_row_state(
                True, self.slider_frame, self.comp_label)
            self.slider.set(2)
            self.comparison_size_label.configure(text=2, state=ctk.DISABLED)
            self.comp_label.configure(state=ctk.DISABLED)
            self.slider.configure(state=ctk.DISABLED)
            self.show_comparison_count()
            self.comparison_count_entry.delete(0, ctk.END)
            self.comparison_count_entry.configure(state=ctk.DISABLED)
            self.comparison_count_label.configure(state=ctk.DISABLED)

        elif value == "Rating":
            self.change_slider_row_state(
                False, self.slider_frame, self.comp_label)
            self.hide_comparison_count()
        else:
            self.change_slider_row_state(
                True, self.slider_frame, self.comp_label)
            self.slider.configure(state=ctk.NORMAL)
            self.comparison_size_label.configure(state=ctk.NORMAL)
            self.comp_label.configure(state=ctk.NORMAL)
            self.comparison_count_entry.configure(state=ctk.NORMAL)
            self.comparison_count_label.configure(state=ctk.NORMAL)
            self.show_comparison_count()

        if self.should_show_rating_options():
            self.show_rating_options()
        else:
            self.hide_rating_options()

        if self.should_show_ranking_options():
            self.show_ranking_options()
        else:
            self.hide_ranking_options()

    def change_slider_row_state(
            self, state: bool, slider_frame: ctk.CTkFrame,
            comp_label: ctk.CTkLabel):
        """
        Changes the state of the slider row.

        Args:
            state (bool): Boolean indicating whether the slider row should be 
                          enabled or disabled.
            slider_frame (CTkFrame): The frame containing the slider.
            comp_label (CTkLabel): The label for comparison size.
        """
        if state:
            comp_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
            slider_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        else:
            comp_label.grid_remove()
            slider_frame.grid_remove()

    def update_comparison_size(self, val: int, label: ctk.CTkLabel):
        """
        Updates the comparison size label based on the slider value.

        Args:
            value (int): The current slider value.
            label (CTkLabel): The label to be updated.
        """
        label.configure(text=int(val))

        if self.should_show_ranking_options():
            self.show_ranking_options()
        else:
            self.hide_ranking_options()

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
        """
        Repopulates the rating buttons list with the current row view.
        """

        for child in self.ratings_list.winfo_children():
            child.destroy()

        for index, button in enumerate(self.rating_buttons):
            self.append_row(index, button)

        add_button = ctk.CTkButton(
            self.ratings_list, text="Add Rating", command=self.add_option)
        add_button.grid(row=len(self.rating_buttons), column=0, pady=3)

    def append_row(self, index: int, button_text: str):
        """
        Adds a row to the rating buttons list

        Args:
            index (int): The index of the row in the list which it is supposed to be
                         added to.
            button_text (str): The currently assigned text of the rating button.
        """

        row = ctk.CTkFrame(self.ratings_list)

        row.grid_columnconfigure(0, weight=1, uniform="row")
        row.grid_columnconfigure(1, weight=1, uniform="row")
        row.grid_columnconfigure(2, weight=1, uniform="row")

        button_value = ctk.CTkLabel(
            row, text="Value: " + str(index),
            font=('Helvetica bold', 20))

        button_frame = ctk.CTkFrame(row)

        if self.edit_index == index:

            text_var = ctk.StringVar(value=button_text)

            text_entry = ctk.CTkEntry(
                row, textvariable=text_var, width=200,
                font=('Helvetica bold', 16))
            text_entry.grid(row=0, column=1, sticky="w")

            ok_button = ctk.CTkButton(
                button_frame, text="Ok", width=56, command=lambda i=index,
                text_var=text_var: self.update_rating(i, text_var))
            cancel_button = ctk.CTkButton(
                button_frame, text="Cancel", width=56, command=self.cancel_edit)

            ok_button.grid(row=0, column=0, sticky="e", padx=5, pady=3)
            cancel_button.grid(row=0, column=1, sticky="e", padx=5, pady=3)
        else:
            button_text = ctk.CTkLabel(
                row, text=button_text,
                font=('Helvetica bold', 20))

            button_up_state = ctk.NORMAL
            button_down_state = ctk.NORMAL

            if index <= 0:
                button_up_state = ctk.DISABLED

            if index >= len(self.rating_buttons) - 1:
                button_down_state = ctk.DISABLED

            button_up = ctk.CTkButton(
                button_frame, text="▲", state=button_up_state, width=28,
                command=lambda i=index: self.move_up(i))
            button_down = ctk.CTkButton(
                button_frame, text="▼", state=button_down_state, width=28,
                command=lambda i=index: self.move_down(i))
            edit_button = ctk.CTkButton(
                button_frame, text="Edit", width=56,
                command=lambda i=index: self.edit(i))
            delete_button = ctk.CTkButton(
                button_frame, text="X", width=28, fg_color="#ed022a",
                hover_color="#bf0021",
                command=lambda i=index: self.delete_rating(i))

            button_text.grid(row=0, column=1, sticky="w", padx=5, pady=3)
            button_up.grid(row=0, column=0, sticky="e", padx=5, pady=3)
            button_down.grid(row=0, column=1, sticky="e", padx=5, pady=3)
            edit_button.grid(row=0, column=2, sticky="e", padx=5, pady=3)
            delete_button.grid(row=0, column=3, sticky="e", padx=5, pady=3)

        button_value.grid(row=0, column=0, sticky="w", padx=5, pady=3)
        button_frame.grid(row=0, column=2, sticky="e", padx=5, pady=3)
        row.grid(row=index, column=0, sticky="ew", pady=3)

    def delete_rating(self, index: int):
        """
        Removes a rating from the list of ratings.

        Args:
            index (int): The index of the rating that is to be removed.
        """

        del (self.rating_buttons[index])
        self.refresh_rating_buttons()

    def move_up(self, index: int):
        """
        Moves a rating up in the list of ratings (decreases its index in the list by 1).
        Other elements are moved accordingly.

        Args:
            index (int): The index of the rating that is to be moved.
        """

        if index > 0:
            temp = self.rating_buttons[index]
            self.rating_buttons[index] = self.rating_buttons[index - 1]
            self.rating_buttons[index - 1] = temp

        self.refresh_rating_buttons()

    def move_down(self, index: int):
        """
        Moves a rating down in the list of ratings (increases its index in the list by 
        1). Other elements are moved accordingly.

        Args:
            index (int): The index of the rating that is to be moved.
        """

        if index < len(self.rating_buttons) - 1:
            temp = self.rating_buttons[index]
            self.rating_buttons[index] = self.rating_buttons[index + 1]
            self.rating_buttons[index + 1] = temp

        self.refresh_rating_buttons()

    def cancel_edit(self):
        """
        Brings (all) rows out of edit mode.        
        """

        self.edit_index = -1
        self.refresh_rating_buttons()

    def update_rating(self, index: int, value: str):
        """
        Updates the text of a rating specified by the index.

        Args:
            index (int): The index of the rating that is to be updated.
            value (str): The new text associated with that rating.
        """

        # make some checks perhaps...
        new_value = value.get()

        self.rating_buttons[index] = new_value

        self.edit_index = -1

        self.refresh_rating_buttons()

    def edit(self, index: int):
        """
        Brings a rating row into edit mode.

        Args:
            index (int): The index of the rating that is to be set to edit mode.
        """

        self.edit_index = index

        self.refresh_rating_buttons()

    def add_option(self):
        """
        Creates a new rating button (and row) and brings it into edit mode.
        """

        self.rating_buttons.append("")
        self.edit_index = len(self.rating_buttons) - 1

        self.refresh_rating_buttons()

    def should_show_rating_options(self):
        """
        Checks if the current selected algorithm implies that rating options should be 
        shown.

        Returns:
            bool: True if rating options should be shown, False otherwise.
        """

        show_rating = self.algorithm_selection.get(
        ) == "Rating" or self.algorithm_selection.get() == "Hybrid"

        return show_rating

    def should_show_ranking_options(self):
        """
        Checks if the current selected algorithm implies that ranking options should be 
        shown.

        Returns:
            bool: True if ranking options should be shown, False otherwise.
        """

        compatible_algorithm = self.algorithm_selection.get(
        ) == "True Skill" or self.algorithm_selection.get(
        ) == "Merge Sort" or self.algorithm_selection.get() == "Hybrid"

        return compatible_algorithm and self.slider.get() == 2

    def should_show_switches(self):
        """
        Checks if the current selected algorithm implies that the user should have the 
        option to add the equal and much greater/smaller ranking buttons.

        Returns:
            bool: True if buttons should be available, False otherwise.
        """

        return self.algorithm_selection.get() != "Merge Sort"

    def create_save(
            self, name: ctk.StringVar, algorithm: sa.SortingAlgorithm,
            comparison_size: ctk.CTkSlider, image_directory: ctk.StringVar,
            scroll_enabled: ctk.BooleanVar):
        """
        Creates and saves the annotation item.

        Args:
            name (StringVar): Name of the annotation item.
            algorithm (SortingAlgorithm): Selected algorithm for sorting 
                                          the images.
            comparison_size (CTkSlider): Slider holding the size of the 
                                         comparison.
            image_directory (StringVar): Directory path containing the 
                                         image files.
            scroll_enabled (BooleanVar): A checkbox with a boolean indicating 
                                         whether scrolling is enabled.
        """

        directory_value = image_directory.get()
        name_value = name.get()
        alg_value = algorithm.get()
        comparison_size_value = int(comparison_size.get())
        scroll_enabled_value = scroll_enabled.get()

        comp_max = None
        if self.comparison_count_entry.get().isnumeric():
            comp_max = int(self.comparison_count_entry.get())

        rating_buttons = None
        rating_prompt = None

        if self.should_show_rating_options():

            if self.rating_buttons:
                rating_buttons = self.rating_buttons

            if self.rating_prompt.get():
                rating_prompt = self.rating_prompt.get()

        custom_rankings = None
        ranking_prompt = None
        if self.should_show_ranking_options():

            custom_rankings = []

            if self.ranking_equals_switch.get():
                custom_rankings.append(self.ranking_buttons[2].get())

            custom_rankings = [self.ranking_buttons[1].get(
            )] + custom_rankings + [self.ranking_buttons[3].get()]

            if self.ranking_much_greater_switch.get():
                custom_rankings = [self.ranking_buttons[0].get(
                )] + custom_rankings + [self.ranking_buttons[4].get()]

            if self.ranking_prompt.get():
                ranking_prompt = self.ranking_prompt.get()

        utils.create_save(
            name_value, alg_value, comparison_size_value, directory_value,
            scroll_enabled_value, rating_buttons, rating_prompt,
            custom_rankings, ranking_prompt, comp_max)

        self.menu_callback()

    def validate(self, value):
        return value.isnumeric() or not value

    def on_invalid(self):
        print("Hold it right there!")
