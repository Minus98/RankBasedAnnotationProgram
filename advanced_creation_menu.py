
import os
import pickle
import random
import sys
import time
from pathlib import Path
from typing import Callable

import customtkinter as ctk
import pandas as pd

import sorting_algorithms as sa


class AdvancedCreationMenu():

    def __init__(
            self, root: ctk.CTk, menu_callback: Callable):

        self.root = root

        self.rating_buttons = ["Rating 1", "Rating 2"]

        self.ranking_buttons = [ctk.StringVar(value="") for _ in range(5)]

        self.basic_settings_frame = ctk.CTkFrame(self.root)
        self.menu_callback = menu_callback
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
            self.switch_frame, text=">>", font=('Helvetica bold', 18), width=70,
            command=self.refresh_ranking_buttons)

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
        self.root.grid_rowconfigure(1, weight=16, uniform="header")
        self.root.grid_rowconfigure(2, weight=2, uniform="header")

        self.name_label.grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

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

        self.edit_index = -1

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

        self.directory_entry.grid(row=3, column=1, padx=10,
                                  pady=(2, 10), sticky="w")

        self.name_entry.grid(row=0, column=1, padx=10,
                             pady=(10, 2), sticky="w")

    def show_ranking_options(self):

        self.ranking_list_frame.grid(
            row=2, column=0, columnspan=2, sticky="ew")

        self.refresh_ranking_buttons()

    def show_rating_options(self):

        self.rating_list_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew")

        self.refresh_rating_buttons()

    def hide_rating_options(self):

        self.rating_list_frame.grid_remove()

    def hide_ranking_options(self):

        self.ranking_list_frame.grid_remove()

    def refresh_ranking_buttons(self):

        for child in self.ranking_list.winfo_children():
            child.destroy()

        current_row = 0

        if self.ranking_equals_switch.get():

            equals_frame = ctk.CTkFrame(master=self.ranking_list)

            self.populate_rank_entry_frame(equals_frame, "A == B:", 2)

            equals_frame.grid(row=current_row, column=0, pady=5, columnspan=2)

            current_row += 1

        # A > B

        A_greater_frame = ctk.CTkFrame(master=self.ranking_list)

        self.populate_rank_entry_frame(A_greater_frame, "A > B:", 1)

        A_greater_frame.grid(row=current_row, column=0, pady=5)

        # A < B

        B_greater_frame = ctk.CTkFrame(master=self.ranking_list)

        self.populate_rank_entry_frame(B_greater_frame, "A < B:", 3)

        B_greater_frame.grid(row=current_row, column=1, pady=5)

        current_row += 1

        if self.ranking_much_greater_switch.get():

            # A >> B

            A_much_greater_frame = ctk.CTkFrame(master=self.ranking_list)

            self.populate_rank_entry_frame(A_much_greater_frame, "A >> B:", 0)

            A_much_greater_frame.grid(row=current_row, column=0, pady=5)

            # A << B

            B_much_greater_frame = ctk.CTkFrame(master=self.ranking_list)

            self.populate_rank_entry_frame(B_much_greater_frame, "A << B:", 4)

            B_much_greater_frame.grid(row=current_row, column=1, pady=5)

            current_row += 1

    def populate_rank_entry_frame(self, frame: ctk.CTkFrame, text: str, var_index: int):

        label = ctk.CTkLabel(
            master=frame, text=text,
            font=('Helvetica bold', 18))

        entry = ctk.CTkEntry(master=frame, width=200,
                             font=('Helvetica bold', 16),
                             textvariable=self.ranking_buttons[var_index])

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        label.grid(row=0, column=0, sticky="e", pady=5, padx=5)
        entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

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

        if self.should_show_rating_options():
            self.show_rating_options()
        else:
            self.hide_rating_options()

        if self.should_show_ranking_options():
            self.show_ranking_options()
        else:
            self.hide_ranking_options()

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

        add_button = ctk.CTkButton(
            self.ratings_list, text="Add Rating", command=self.add_option)
        add_button.grid(row=len(self.rating_buttons), column=0, pady=3)

    def append_row(self, index, button):

        row = ctk.CTkFrame(self.ratings_list)

        row.grid_columnconfigure(0, weight=1, uniform="row")
        row.grid_columnconfigure(1, weight=1, uniform="row")
        row.grid_columnconfigure(2, weight=1, uniform="row")

        button_value = ctk.CTkLabel(
            row, text="Value: " + str(index),
            font=('Helvetica bold', 20))

        button_frame = ctk.CTkFrame(row)

        if self.edit_index == index:

            text_var = ctk.StringVar(value=button)

            text_entry = ctk.CTkEntry(
                row, textvariable=text_var, width=200, font=('Helvetica bold', 16))
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
                row, text=button,
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

    def cancel_edit(self):

        self.edit_index = -1
        self.refresh_rating_buttons()

    def update_rating(self, index, value):

        # make some checks perhaps...
        new_value = value.get()

        self.rating_buttons[index] = new_value

        self.edit_index = -1

        self.refresh_rating_buttons()

    def edit(self, index):

        self.edit_index = index

        self.refresh_rating_buttons()

    def add_option(self):

        self.rating_buttons.append("")
        self.edit_index = len(self.rating_buttons) - 1

        self.refresh_rating_buttons()

    def should_show_rating_options(self):

        show_rating = self.algorithm_selection.get(
        ) == "Rating" or self.algorithm_selection.get() == "Hybrid"

        return show_rating

    def should_show_ranking_options(self):

        show_ranking = self.algorithm_selection.get(
        ) == "True Skill" or self.algorithm_selection.get(
        ) == "Merge Sort" or self.algorithm_selection.get() == "Hybrid"

        return show_ranking

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
            pop_out (CTkToplevel): The pop-out window.
            scroll_enabled (BooleanVar): A checkbox with a boolean indicating 
            whether scrolling is enabled.
        """

        directory = os.path.relpath(image_directory.get())
        final_name = name.get()

        img_paths = list(str(os.path.basename(p))
                         for p in Path(directory).glob("**/*")
                         if p.suffix
                         in {'.jpg', '.png', '.nii'} and 'sorted'
                         not in str(p).lower())

        random.shuffle(img_paths)

        alg = algorithm.get()

        if alg == "Merge Sort":
            sort_alg = sa.MergeSort(data=img_paths)
        elif alg == "Rating":
            sort_alg = sa.RatingAlgorithm(data=img_paths)
        elif alg == "Hybrid":
            sort_alg = sa.HybridTrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))
        else:
            sort_alg = sa.TrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))

        file_name = str(int(time.time()))

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        path = application_path + "/saves"

        if not os.path.exists(path):
            os.makedirs(path)

        path_to_save = path + "/" + file_name

        df = pd.DataFrame(
            columns=['result', 'diff_levels', 'time', 'session', 'user',
                     'undone', 'type'])

        df.to_csv(path_to_save + ".csv", index=False)

        rel_path_to_save = "saves/" + file_name
        save_obj = {
            "sort_alg": sort_alg,
            "name": final_name,
            "image_directory": directory,
            "path_to_save": rel_path_to_save,
            "user_directory_dict": {},
            "scroll_allowed": scroll_enabled.get()}

        if self.should_show_rating_options():

            if self.rating_buttons:
                save_obj["custom_ratings"] = self.rating_buttons

            if self.rating_prompt.get():
                save_obj["custom_rating_prompt"] = self.rating_prompt.get()

        if self.should_show_ranking_options():

            custom_rankings = []

            if self.ranking_equals_switch.get():
                custom_rankings.append(self.ranking_buttons[2].get())

            custom_rankings = [self.ranking_buttons[1].get(
            )] + custom_rankings + [self.ranking_buttons[3].get()]

            if self.ranking_much_greater_switch.get():
                custom_rankings = [self.ranking_buttons[0].get(
                )] + custom_rankings + [self.ranking_buttons[4].get()]

            save_obj["custom_rankings"] = custom_rankings

            if self.ranking_prompt.get():
                save_obj["custom_ranking_prompt"] = self.ranking_prompt.get()

        f = open(path + "/" + file_name + ".pickle", "wb")
        pickle.dump(save_obj, f)
        f.close()

        self.menu_callback()
