import customtkinter as ctk
from pathlib import Path
from sorting_algorithms import *
import os
import pickle
from creation_pop_out import CreationPopOut
import sys
from utils import *


class MenuScreen():

    def __init__(self, root, creation_callback, ordering_callback, center):

        self.root = root

        self.creation_callback = creation_callback
        self.ordering_callback = ordering_callback
        self.center = center

        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.dirname(__file__)

        path = application_path + "/Saves"

        self.paths = list(Path(path).glob('*.pickle'))

        self.saves = [pickle.load(open(path, 'rb')) for path in self.paths]

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation", font=('Helvetica bold', 40))

        self.menu_frame = ctk.CTkFrame(master=self.root)

        self.instructions_frame = ctk.CTkFrame(master=self.root)

        self.new_button = ctk.CTkButton(
            master=self.menu_frame, text="New Annotation", width=250, height=45, font=('Helvetica bold', 20), command=self.new_annotation)
        self.delete_button = ctk.CTkButton(
            master=self.menu_frame, text="Delete Annotation", width=250, height=45, font=('Helvetica bold', 20))

        self.saved_annotations_header = ctk.CTkFrame(
            master=self.menu_frame, corner_radius=0, fg_color=self.menu_frame.cget("fg_color"))

        self.saved_annotations_header.grid_columnconfigure(
            0, weight=1, uniform="header")
        self.saved_annotations_header.grid_columnconfigure(
            1, weight=1, uniform="header")
        self.saved_annotations_header.grid_columnconfigure(
            2, weight=1, uniform="header")
        self.saved_annotations_header.grid_rowconfigure(
            0, weight=1, uniform="header")

        self.header_name_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Name:", font=('Helvetica bold', 20))

        self.header_algorithm_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Algorithm:", font=('Helvetica bold', 20))

        self.header_images_label = ctk.CTkLabel(
            master=self.saved_annotations_header, text="Images:", font=('Helvetica bold', 20))

        self.saved_annotations_frame = ctk.CTkScrollableFrame(
            master=self.menu_frame, height=400)

        self.saved_annotations_frame.columnconfigure(0, weight=1)

        b = "•"

        self.text = ctk.CTkLabel(master=self.instructions_frame, text="Welcome to the Rank-Based Annotation program \n   " +
                                 b + " Order the images youngest to oldest, left to right \n     " +
                                 b + " Specify the difference between two images using the radio buttons", font=('Helvetica bold', 20), wraplength=400)

    def display(self):

        self.root.grid_rowconfigure(0, weight=1, uniform="header")
        self.root.grid_rowconfigure(1, weight=8, uniform="header")
        self.root.grid_columnconfigure(0, weight=2)
        self.root.grid_columnconfigure(1, weight=1)

        self.header.grid(row=0, column=0, columnspan=2, sticky="S")
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

        self.new_button.grid(row=2, column=0, padx=(
            20, 10), pady=10)
        self.delete_button.grid(row=2, column=1, padx=(
            10, 20), pady=10)

        self.saved_annotations_header.grid(
            row=0, column=0, columnspan=2, sticky="sew", padx=(10, 20), pady=(20, 0))

        self.header_name_label.grid(
            row=0, column=0, sticky="w", padx=10, pady=4)
        self.header_algorithm_label.grid(
            row=0, column=1, sticky="w", padx=10, pady=4)
        self.header_images_label.grid(
            row=0, column=2, sticky="w", padx=10, pady=4)

        self.saved_annotations_frame.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 0))

        self.display_saves()

        self.text.grid(row=0, column=0, padx=10, pady=10, sticky="new")

    def display_saves(self):

        for i, save in enumerate(self.saves):
            self.append_row(i, save)

    def append_row(self, index, save):

        saved_annotations_row = ctk.CTkFrame(
            master=self.saved_annotations_frame)

        saved_annotations_row.bind(
            "<Button-1>", command=lambda event, i=index: self.load_save(i))

        saved_annotations_row.grid(row=index, column=0, sticky="ew", pady=3)

        saved_annotations_row.grid_columnconfigure(0, weight=1, uniform="row")
        saved_annotations_row.grid_columnconfigure(1, weight=1, uniform="row")
        saved_annotations_row.grid_columnconfigure(2, weight=1, uniform="row")
        saved_annotations_row.grid_rowconfigure(0, weight=1, uniform="row")

        save_name_label = ctk.CTkLabel(
            master=saved_annotations_row, text=save["name"], font=('Helvetica bold', 20))
        save_name_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        sort_alg = save["sort_alg"]

        algorithm_label = ctk.CTkLabel(
            master=saved_annotations_row, text=type(sort_alg).__name__, font=('Helvetica bold', 20))

        algorithm_label.grid(row=0, column=1, padx=10, pady=4, sticky="w")

        total_images = len(sort_alg.data)

        total_images_label = ctk.CTkLabel(
            master=saved_annotations_row, text=total_images, font=('Helvetica bold', 20))

        total_images_label.grid(row=0, column=2, padx=10, pady=4, sticky="w")

        for child in saved_annotations_row.winfo_children():
            child.bind("<Button-1>", command=lambda event,
                       i=index: self.load_save(i))

        add_hover(saved_annotations_row)

    def new_annotation(self):
        CreationPopOut(self.creation_callback, self.center)

    def load_save(self, index):

        file = open(self.paths[index], 'rb')

        save_obj = pickle.load(file)

        self.ordering_callback(save_obj)
