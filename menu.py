import customtkinter as ctk
from pathlib import Path
from sorting_algorithms import *
import os
import pickle
from creation_pop_out import CreationPopOut


class MenuScreen():

    def __init__(self, root, creation_callback, ordering_callback, center):

        self.root = root

        self.creation_callback = creation_callback
        self.ordering_callback = ordering_callback
        self.center = center

        self.paths = list(Path("Saves").glob('*.pickle'))

        self.menu_frame = ctk.CTkFrame(master=self.root)

        self.instructions_frame = ctk.CTkFrame(master=self.root)

        self.new_button = ctk.CTkButton(
            master=self.menu_frame, text="New Annotation", width=200, height=40, font=('Helvetica bold', 20), command=self.new_annotation)
        self.delete_button = ctk.CTkButton(
            master=self.menu_frame, text="Delete Annotation", width=200, height=40, font=('Helvetica bold', 20))

        self.saved_annotations_frame = ctk.CTkScrollableFrame(
            master=self.menu_frame, height=400)

        self.saved_annotations_frame.columnconfigure(0, weight=1)

        b = "•"

        self.text = ctk.CTkLabel(master=self.instructions_frame, text="Welcome to the Rank-Based Annotation program \n   " +
                                 b + " Order the images youngest to oldest, left to right \n     " +
                                 b + " Specify the difference between two images using the radio buttons", font=('Helvetica bold', 20), wraplength=400)

    def display(self):

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.menu_frame.grid(row=0, column=0, sticky="nsew",
                             padx=(20, 10), pady=20)
        self.instructions_frame.grid(
            row=0, column=1, sticky="nsew", padx=(20, 10), pady=20)

        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_columnconfigure(1, weight=1)
        self.menu_frame.grid_rowconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(1, weight=2)

        self.new_button.grid(row=0, column=0, padx=(
            20, 10), pady=10, sticky="sew")
        self.delete_button.grid(row=0, column=1, padx=(
            10, 20), pady=10, sticky="sew")

        self.saved_annotations_frame.grid(
            row=1, column=0, columnspan=2, sticky="new", padx=10, pady=10)

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

        self.add_hover(saved_annotations_row)

    def new_annotation(self):
        CreationPopOut(self.creation_callback, self.center)

    def load_save(self, index):

        file = open(self.paths[index], 'rb')

        save_obj = pickle.load(file)

        self.ordering_callback(save_obj)

    def add_hover(self, widget):

        self.add_hover_to_children(widget, widget)

    def add_hover_to_children(self, widget, child_widget):

        child_widget.bind("<Enter>", lambda event,
                          widget=widget, color=widget.cget("fg_color"): self.highlight(widget, color))
        child_widget.bind("<Leave>", lambda event,
                          widget=widget, color=widget.cget("fg_color"): self.remove_highlight(widget, color))

        for child in child_widget.winfo_children():
            self.add_hover_to_children(widget, child)

    def highlight(self, widget, color):

        gray_color = int(color[1][-2:]) + 10

        if gray_color > 100:
            gray_color = 100

        widget.configure(fg_color='gray' + str((gray_color)))

    def remove_highlight(self, widget, color):
        # might have to change so that it is recursive like highlight...
        widget.configure(fg_color=color)
