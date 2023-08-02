from pathlib import Path
from typing import Callable

import customtkinter as ctk

import utils.saves_handler as saves_handler
import utils.ctk_utils as ctk_utils
from sorting_algorithms import SortingAlgorithm


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
        self.advanced_settings_callback = advanced_settings_callback
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

        ctk.CTkLabel(master=pop_out, text="Name:", font=('Helvetica bold', 20)).grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        self.name = ctk.StringVar()

        ctk.CTkEntry(
            master=pop_out, textvariable=self.name,
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

        self.comparison_size_label = ctk.CTkLabel(master=slider_frame, font=(
            'Helvetica bold', 25))

        self.slider = ctk.CTkSlider(
            master=slider_frame, from_=2, to=4, number_of_steps=2,
            command=lambda val,
            label=self.comparison_size_label: self.update_comparison_size(
                val, label))

        self.slider.set(2)

        self.slider.grid(row=0, column=0)

        self.comparison_size_label.configure(text=int(self.slider.get()))

        self.comparison_size_label.grid(row=0, column=1, padx=5)

        self.algorithm_selection = ctk.CTkOptionMenu(
            master=pop_out,
            values=["True Skill", "Merge Sort", "Rating", "Hybrid"],
            width=200, height=40, font=('Helvetica bold', 20),
            command=lambda value, pop_out=pop_out, slider=self.slider,
            slider_frame=slider_frame, label=self.comparison_size_label,
            comp_label=comp_label: self.algorithm_changed(
                value, pop_out, slider, slider_frame, label, comp_label))

        self.algorithm_selection.grid(
            row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(
            master=pop_out, text="Image Directory:",
            font=('Helvetica bold', 20)).grid(
            row=3, column=0, padx=10, pady=(2, 10),
            sticky="e")

        self.image_directory = ctk.StringVar()
        self.image_directory.set(str(Path("data/Images").resolve()))

        self.directory_entry = ctk.CTkEntry(
            master=pop_out, textvariable=self.image_directory,
            placeholder_text="select the directory which contains the files",
            width=400, height=40, font=('Helvetica bold', 16),
            state=ctk.DISABLED)

        self.directory_entry.bind(
            "<Button-1>", command=lambda event, pop_out=pop_out,
            image_directory=self.image_directory: self.select_directory(
                pop_out, image_directory))

        self.directory_entry.grid(row=3, column=1, padx=10,
                                  pady=(2, 10), sticky="w")

        ctk.CTkLabel(
            master=pop_out, text="Enable Scrolling:",
            font=('Helvetica bold', 20)).grid(
            row=4, column=0, padx=10, pady=2, sticky="e")
        self.scroll_enabled = ctk.BooleanVar()
        self.scroll_enabled_checkbox = ctk.CTkCheckBox(
            master=pop_out, variable=self.scroll_enabled, text="",
            checkbox_width=30, checkbox_height=30, onvalue=True,
            offvalue=False)
        self.scroll_enabled_checkbox.grid(
            row=4, column=1, padx=10, pady=2, sticky="w")

        button_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        button_frame.grid(row=5, column=0, columnspan=2,
                          sticky="ew", pady=(0, 10))

        create_button = ctk.CTkButton(
            master=button_frame, text="Create Annotation", width=200,
            height=40, font=('Helvetica bold', 20),
            command=lambda name=self.name,
            algorithm_selection=self.algorithm_selection, slider=self.slider,
            image_directory=self.image_directory, pop_out=pop_out,
            scroll_enabled=self.scroll_enabled: self.create_save(
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
            "<Enter>", lambda event: ctk_utils.highlight_label(
                self.advanced_label))
        self.advanced_label.bind(
            "<Leave>", lambda event: ctk_utils.remove_highlight_label(
                self.advanced_label))
        self.advanced_label.bind(
            "<Button-1>", lambda event: self.transition_to_advanced())

        self.advanced_label.place(relx=0.98, rely=0.02, anchor="ne")

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)

    def transition_to_advanced(self):

        current_field_values = {}

        if self.name.get():
            current_field_values['name'] = self.name.get(
            )

        if self.algorithm_selection.get():
            current_field_values['algorithm_selection'] = self.algorithm_selection.get(
            )

        if self.image_directory.get():
            current_field_values['image_directory'] = self.image_directory.get(
            )

        if self.slider.get():
            current_field_values['slider'] = self.slider.get()

        if self.scroll_enabled.get():
            current_field_values['scroll_enabled'] = self.scroll_enabled.get()

        self.advanced_settings_callback(current_field_values)

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

        directory_value = image_directory.get()
        name_value = name.get()
        alg_value = algorithm.get()
        comparison_size_value = int(comparison_size.get())
        scroll_enabled_value = scroll_enabled.get()

        saves_handler.create_save(
            name_value, alg_value, comparison_size_value, directory_value,
            scroll_enabled_value)

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
        current_dir = directory_var.get()
        res_directory = ctk.filedialog.askdirectory(
            parent=root, initialdir=current_dir)
        if res_directory:
            directory_var.set(res_directory)
