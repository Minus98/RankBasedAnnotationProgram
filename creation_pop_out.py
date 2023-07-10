import os
import pickle
import random
import sys
import time
from pathlib import Path
from typing import Callable

import customtkinter as ctk
import pandas as pd

import utils
from sorting_algorithms import (HybridTrueSkill, MergeSort, RatingAlgorithm,
                                SortingAlgorithm, TrueSkill)


class CreationPopOut():
    """
    Class representing a pop-up window for creating an annotation session.
    """

    def __init__(self, creation_callback: Callable, center: Callable, 
                 advanced_settings_callback: Callable):
        """
        Initializes the CreationPopOut instance.

        Args:
            creation_callback (function): Callback function to be executed after 
            creating the annotation.
            center (function): Function to center the pop-up window.
            advanced_settings_callback (function): Calback function to bring up the
            advanced settings menu.
        """

        self.creation_callback = creation_callback
        self.center = center

        pop_out = ctk.CTkToplevel()

        w = 700
        h = 400
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))

        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=2)

        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=2, weight=1)
        pop_out.rowconfigure(index=3, weight=1)
        pop_out.rowconfigure(index=4, weight=1)
        pop_out.rowconfigure(index=5, weight=1)

        self.selected_algorithm = ctk.StringVar()

        ctk.CTkLabel(master=pop_out, text="Name:", font=('Helvetica bold', 20)).grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        name = ctk.StringVar()

        ctk.CTkEntry(
            master=pop_out, textvariable=name,
            placeholder_text="Enter the name of the annotation session",
            width=200, height=40, font=('Helvetica bold', 20)).grid(
            row=0, column=1, padx=10, pady=(10, 2),
            sticky="w")

        ctk.CTkLabel(master=pop_out, text="Algorithm:", font=(
            'Helvetica bold', 20)).grid(row=1, column=0, padx=10, pady=2, sticky="e")

        comp_label = ctk.CTkLabel(
            master=pop_out, text="Comparison Size:",
            font=('Helvetica bold', 20))

        comp_label.grid(
            row=2, column=0, padx=10, pady=2, sticky="e")

        slider_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        slider_frame.grid(
            row=2, column=1, padx=10, pady=2, sticky="w")

        comparison_count_label = ctk.CTkLabel(master=slider_frame, font=(
            'Helvetica bold', 25))

        slider = ctk.CTkSlider(
            master=slider_frame, from_=2, to=4, number_of_steps=2,
            command=lambda val,
            label=comparison_count_label: self.update_comparison_size(
                val, label))

        slider.set(2)

        slider.grid(row=0, column=0)

        comparison_count_label.configure(text=int(slider.get()))

        comparison_count_label.grid(row=0, column=1, padx=5)

        algorithm_selection = ctk.CTkOptionMenu(
            master=pop_out,
            values=["True Skill", "Merge Sort", "Rating", "Hybrid"],
            width=200, height=40, font=('Helvetica bold', 20),
            command=lambda value, pop_out=pop_out, slider=slider,
            slider_frame=slider_frame, label=comparison_count_label,
            comp_label=comp_label: self.algorithm_changed(
                value, pop_out, slider, slider_frame, label, comp_label))

        algorithm_selection.grid(
            row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(
            master=pop_out, text="Image Directory:",
            font=('Helvetica bold', 20)).grid(
            row=3, column=0, padx=10, pady=(2, 10),
            sticky="e")

        image_directory = ctk.StringVar()
        image_directory.set(str(Path("data/Images").resolve()))

        directory_entry = ctk.CTkEntry(
            master=pop_out, textvariable=image_directory,
            placeholder_text="select the directory which contains the files",
            width=400, height=40, font=('Helvetica bold', 16),
            state=ctk.DISABLED)

        directory_entry.bind(
            "<Button-1>", command=lambda event, pop_out=pop_out,
            image_directory=image_directory: self.select_directory(
                pop_out, image_directory))

        directory_entry.grid(row=3, column=1, padx=10,
                             pady=(2, 10), sticky="w")

        ctk.CTkLabel(
            master=pop_out, text="Enable Scrolling:",
            font=('Helvetica bold', 20)).grid(
            row=4, column=0, padx=10, pady=2, sticky="e")
        scroll_enabled = ctk.BooleanVar()
        scroll_enabled_checkbox = ctk.CTkCheckBox(
            master=pop_out, variable=scroll_enabled, text="",
            checkbox_width=30, checkbox_height=30, onvalue=True,
            offvalue=False)
        scroll_enabled_checkbox.grid(
            row=4, column=1, padx=10, pady=2, sticky="w")

        button_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        button_frame.grid(row=5, column=0, columnspan=2,
                          sticky="ew", pady=(0, 10))

        create_button = ctk.CTkButton(
            master=button_frame, text="Create Annotation", width=200,
            height=40, font=('Helvetica bold', 20),
            command=lambda name=name, algorithm_selection=algorithm_selection,
            slider=slider, image_directory=image_directory, pop_out=pop_out,
            scroll_enabled=scroll_enabled: self.create_save(
                name, algorithm_selection, slider, image_directory, pop_out,
                scroll_enabled))
        delete_button = ctk.CTkButton(
            master=button_frame, text="Cancel", width=200, height=40,
            font=('Helvetica bold', 20),
            command=pop_out.destroy)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        create_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        delete_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.advanced_label = ctk.CTkLabel(
            master=pop_out, text="Advanced Settings",
            font=('Helvetica bold', 20),
            text_color="#777777")

        self.advanced_label.bind(
            "<Enter>", lambda event: utils.highlight_label(self.advanced_label))
        self.advanced_label.bind(
            "<Leave>", lambda event: utils.remove_highlight_label(
                self.advanced_label))
        self.advanced_label.bind(
            "<Button-1>", lambda event: advanced_settings_callback())

        self.advanced_label.place(relx=0.98, rely=0.02, anchor = "ne")

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)

    def create_save(
            self, name: ctk.StringVar, algorithm: SortingAlgorithm,
            comparison_size: ctk.CTkSlider, image_directory: ctk.StringVar,
            pop_out: ctk.CTkToplevel, scroll_enabled: ctk.BooleanVar):
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
            sort_alg = MergeSort(data=img_paths)
        elif alg == "Rating":
            sort_alg = RatingAlgorithm(data=img_paths)
        elif alg == "Hybrid":
            sort_alg = HybridTrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))
        else:
            sort_alg = TrueSkill(
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

        f = open(path + "/" + file_name + ".pickle", "wb")
        pickle.dump(save_obj, f)
        f.close()

        pop_out.destroy()

        self.creation_callback()

    def algorithm_changed(
            self, value: str, pop_out: ctk.CTkToplevel, slider: ctk.CTkSlider,
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
                True, pop_out, slider_frame, comp_label)
            slider.set(2)
            label.configure(text=2, state=ctk.DISABLED)
            comp_label.configure(state=ctk.DISABLED)
            slider.configure(state=ctk.DISABLED)

        elif value == "Rating":
            self.change_slider_row_state(
                False, pop_out, slider_frame, comp_label)

        else:
            self.change_slider_row_state(
                True, pop_out, slider_frame, comp_label)
            slider.configure(state=ctk.NORMAL)
            label.configure(state=ctk.NORMAL)
            comp_label.configure(state=ctk.NORMAL)

    def change_slider_row_state(
            self, state: bool, pop_out: ctk.CTkToplevel,
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
            pop_out.rowconfigure(index=2, weight=1)

        else:
            comp_label.grid_remove()
            slider_frame.grid_remove()
            pop_out.rowconfigure(index=2, weight=0)

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
