import customtkinter as ctk
import pickle
import time
from pathlib import Path
import random

import pandas as pd
from sorting_algorithms import *
import os
import sys


class CreationPopOut():

    def __init__(self, creation_callback, center):

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

        self.selected_algorithm = ctk.StringVar()

        ctk.CTkLabel(master=pop_out, text="Name:", font=('Helvetica bold', 20)).grid(
            row=0, column=0, padx=10, pady=(10, 2), sticky="e")

        name = ctk.StringVar()

        ctk.CTkEntry(master=pop_out, textvariable=name,
                     placeholder_text="Enter the name of the annotation session", width=200, height=40, font=('Helvetica bold', 20)).grid(row=0, column=1, padx=10, pady=(10, 2), sticky="w")

        ctk.CTkLabel(master=pop_out, text="Algorithm:", font=('Helvetica bold', 20)).grid(
            row=1, column=0, padx=10, pady=2, sticky="e")

        comp_label = ctk.CTkLabel(
            master=pop_out, text="Comparison Size:", font=('Helvetica bold', 20))

        comp_label.grid(
            row=2, column=0, padx=10, pady=2, sticky="e")

        slider_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        slider_frame.grid(
            row=2, column=1, padx=10, pady=2, sticky="w")

        comparison_count_label = ctk.CTkLabel(master=slider_frame, font=(
            'Helvetica bold', 25))

        slider = ctk.CTkSlider(master=slider_frame, from_=2,
                               to=4, number_of_steps=2, command=lambda val, label=comparison_count_label: self.update_comparison_size(val, label))

        slider.set(2)

        slider.grid(row=0, column=0)

        comparison_count_label.configure(text=int(slider.get()))

        comparison_count_label.grid(row=0, column=1, padx=5)

        algorithm_selection = ctk.CTkOptionMenu(
            master=pop_out, values=["True Skill", "Merge Sort"], width=200, height=40, font=('Helvetica bold', 20), command=lambda value, slider=slider, label=comparison_count_label, comp_label=comp_label: self.algorithm_changed(value, slider, label, comp_label))

        algorithm_selection.grid(
            row=1, column=1, padx=10, pady=2, sticky="w")

        ctk.CTkLabel(master=pop_out, text="Image Directory:", font=('Helvetica bold', 20)).grid(
            row=3, column=0, padx=10, pady=(2, 10), sticky="e")

        image_directory = ctk.StringVar()
        image_directory.set(str(Path("Images").resolve()))

        directory_entry = ctk.CTkEntry(
            master=pop_out, textvariable=image_directory, placeholder_text="select the directory which contains the files", width=400, height=40, font=('Helvetica bold', 16), state=ctk.DISABLED)

        directory_entry.bind("<Button-1>", command=lambda event,
                             image_directory=image_directory: self.select_directory(event, image_directory))

        directory_entry.grid(row=3, column=1, padx=10,
                             pady=(2, 10), sticky="w")

        button_frame = ctk.CTkFrame(
            master=pop_out, fg_color=pop_out.cget("fg_color"))
        button_frame.grid(row=4, column=0, columnspan=2,
                          sticky="ew", pady=(0, 10))

        create_button = ctk.CTkButton(
            master=button_frame, text="Create Annotation", width=200, height=40, font=('Helvetica bold', 20), command=lambda name=name, algorithm_selection=algorithm_selection, slider=slider, image_directory=image_directory, pop_out=pop_out: self.create_save(name, algorithm_selection, slider, image_directory, pop_out))
        delete_button = ctk.CTkButton(
            master=button_frame, text="Cancel", width=200, height=40, font=('Helvetica bold', 20), command=pop_out.destroy)

        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        create_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        delete_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        pop_out.grab_set()

    def create_save(self, name, algorithm, comparison_size, image_directory, pop_out):

        directory = os.path.relpath(image_directory.get())
        final_name = name.get()

        img_paths = [os.path.join(directory, f) for f in os.listdir(
            directory) if os.path.isfile(os.path.join(directory, f))]

        random.shuffle(img_paths)

        alg = algorithm.get()

        if alg == "Merge Sort":
            sort_alg = MergeSort(data=img_paths)
        else:
            sort_alg = TrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))

        file_name = str(int(time.time()))

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        path = application_path + "/Saves"
        if not os.path.exists(path):
            os.makedirs(path)

        path_to_save = path + "/" + file_name

        df = pd.DataFrame(
            columns=['result', 'diff_levels', 'time', 'session', 'user', 'undone'])

        output_path = path_to_save + ".csv"
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))

        save_obj = {"sort_alg": sort_alg, "name": final_name,
                    "image_directory": directory, "path_to_save": path_to_save}

        f = open(path + "/" + file_name + ".pickle", "wb")
        pickle.dump(save_obj, f)
        f.close()

        pop_out.destroy()

        self.creation_callback()

    def algorithm_changed(self, value, slider, label, comp_label):

        if value == "Merge Sort":
            slider.set(2)
            label.configure(text=2, state=ctk.DISABLED)
            comp_label.configure(state=ctk.DISABLED)
            slider.configure(state=ctk.DISABLED)
        else:
            slider.configure(state=ctk.NORMAL)
            label.configure(state=ctk.NORMAL)
            comp_label.configure(state=ctk.NORMAL)

    def update_comparison_size(self, val, label):
        label.configure(text=int(val))

    def select_directory(self, event, directory_var):
        directory = ctk.filedialog.askdirectory()
        directory_var.set(directory)
