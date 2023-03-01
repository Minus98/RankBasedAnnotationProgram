import customtkinter as ctk
from pathlib import Path
from sorting_algorithms import *
import os
import time
import pickle


class MenuScreen():

    def __init__(self, root, creation_callback, ordering_callback):

        self.root = root

        self.creation_callback = creation_callback
        self.ordering_callback = ordering_callback

        self.paths = list(Path("Saves").glob('*.pickle'))

        self.menu_frame = ctk.CTkFrame(master=self.root)

        self.instructions_frame = ctk.CTkFrame(master=self.root)

        self.new_button = ctk.CTkButton(
            master=self.menu_frame, text="New Annotation", width=200, height=40, font=('Helvetica bold', 20), command=self.new_annotation)
        self.delete_button = ctk.CTkButton(
            master=self.menu_frame, text="Delete Annotation", width=200, height=40, font=('Helvetica bold', 20))

        self.saved_annotations_frame = ctk.CTkScrollableFrame(
            master=self.menu_frame)

        self.saved_annotations_frame.columnconfigure(0, weight=1)

        b = "•"

        self.text = ctk.CTkLabel(master=self.instructions_frame, text="Welcome to the Rank-Based Annotation program \n   " +
                                 b + " Order the images youngest to oldest, left to right \n     " +
                                 b + " Specify the difference between two images using the radio buttons", font=('Helvetica bold', 20))

    def display(self):

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.menu_frame.grid(row=0, column=0)
        self.instructions_frame.grid(row=0, column=1)

        self.new_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        self.delete_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.saved_annotations_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        self.display_saves()

        self.text.grid(row=0, column=0, padx=10, pady=10)

    def display_saves(self):

        for i, path in enumerate(self.paths):
            filename, _ = os.path.splitext(os.path.basename(path))
            self.append_row(i, filename)

    def append_row(self, index, name):

        saved_annotations_row = ctk.CTkFrame(
            master=self.saved_annotations_frame)

        saved_annotations_row.bind(
            "<Button-1>", command=lambda event, i=index: self.load_save(i))

        saved_annotations_row.grid(row=index, column=0, sticky="ew", pady=3)

        save_name_label = ctk.CTkLabel(
            master=saved_annotations_row, text=name, font=('Helvetica bold', 20))
        save_name_label.grid(row=0, column=0, padx=5, pady=2)

    def new_annotation(self):
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
        image_directory.set("/Images")
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

        directory = image_directory.get()
        final_name = name.get()

        img_paths = [str(path)
                     for path in list(Path(directory).glob('*.jpg'))]
        random.shuffle(img_paths)

        alg = algorithm.get()

        if alg == "Merge Sort":
            sort_alg = MergeSort(data=img_paths)
        else:
            sort_alg = TrueSkill(
                data=img_paths, comparison_size=int(comparison_size.get()))

        file_name = name.get() + "_" + str(int(time.time()))
        save_obj = {"sort_alg": sort_alg, "name": final_name,
                    "image_directory": directory, "path_to_save": file_name}

        f = open("Saves/" + file_name + ".pickle", "wb")
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
            #pop_out.rowconfigure(index=1, weight=0)

    def update_comparison_size(self, val, label):
        label.configure(text=int(val))

    def select_directory(self, event, directory_var):
        directory = ctk.filedialog.askdirectory()
        directory_var.set(directory)

    def load_save(self, index):

        file = open(self.paths[index], 'rb')

        save_obj = pickle.load(file)

        #self.sort_alg = self.save_obj["sort_alg"]

        #self.comparison_size = self.sort_alg.comparison_size

        self.ordering_callback(save_obj)

    def center(self, w, h):
        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40

        return x, y
