import random
import customtkinter as ctk
from helper_functions import DiffLevel
import time
import pandas as pd
from is_finished_pop_out import IsFinishedPopOut
import sorting_algorithms as sa
from utils import *
from ordering import OrderingScreen


class RatingScreen(OrderingScreen):

    def __init__(self, root, save_obj, menu_callback, center, user):

        super().__init__(root, save_obj, menu_callback, center, user)

        self.buttons_frame = ctk.CTkFrame(master=self.root)

        self.question = ctk.CTkLabel(
            master=self.root, text="The bronchial wall thickening in the image appears to be ... ", font=('Helvetica bold', 20))

        self.none_button = ctk.CTkButton(master=self.buttons_frame, text="None (1)", width=160,
                                         height=40, command=lambda: self.submit(0), font=('Helvetica bold', 20))
        self.mild_button = ctk.CTkButton(master=self.buttons_frame, text="Mild (2)", width=160,
                                         height=40, command=lambda: self.submit(1), font=('Helvetica bold', 20))
        self.moderate_button = ctk.CTkButton(master=self.buttons_frame, text="Moderate (3)", width=160,
                                             height=40, command=lambda: self.submit(2), font=('Helvetica bold', 20))
        self.severe_button = ctk.CTkButton(master=self.buttons_frame, text="Severe (4)", width=160,
                                           height=40, command=lambda: self.submit(3), font=('Helvetica bold', 20))

        self.tab_items = [self.none_button, self.mild_button,
                          self.moderate_button, self.severe_button]
        self.tab_index = -1

        self.root.bind(
            "1", lambda event: self.on_shortcmd(0))
        self.root.bind(
            "2", lambda event: self.on_shortcmd(1))
        self.root.bind(
            "3", lambda event: self.on_shortcmd(2))
        self.root.bind(
            "4", lambda event: self.on_shortcmd(3))

        self.root.bind("<KeyRelease-1>", lambda event: self.on_shortcmd_up(0))
        self.root.bind("<KeyRelease-2>", lambda event: self.on_shortcmd_up(1))
        self.root.bind("<KeyRelease-3>", lambda event: self.on_shortcmd_up(2))
        self.root.bind("<KeyRelease-4>", lambda event: self.on_shortcmd_up(3))

        self.root.bind(
            "<Return>", lambda event: self.on_enter())

        self.root.bind(
            "<Tab>", lambda event: self.on_tab())

    def display(self):

        self.session_start_time = time.time()
        self.session_elapsed_time_prev = 0

        self.root.grid_rowconfigure(0, weight=3, uniform="ordering")
        self.root.grid_rowconfigure(1, weight=26, uniform="ordering")
        self.root.grid_rowconfigure(2, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(3, weight=2, uniform="ordering")
        self.root.grid_rowconfigure(4, weight=4, uniform="ordering")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.images_frame.grid(row=1, column=0, columnspan=2, padx=0, pady=0)

        self.question.grid(row=3, column=0, columnspan=2, pady=10, sticky="S")

        self.buttons_frame.grid(row=4, column=0, columnspan=2, sticky="N")

        self.none_button.grid(row=0, column=0, padx=(10, 5), pady=10)
        self.mild_button.grid(row=0, column=1, padx=5, pady=10)
        self.moderate_button.grid(row=0, column=2, padx=5, pady=10)
        self.severe_button.grid(row=0, column=3, padx=5, pady=10)

        self.session_duration_label.place(relx=0.98, y=20, anchor="ne")

        self.comp_count_label.grid(row=0, column=0, columnspan=2, sticky="S")

        self.back_button.place(x=20, y=20)

        self.timer_after = self.root.after(1000, self.update_time)

        if not self.is_finished_check():
            self.display_new_comparison()

    def init_image_frames(self):

        self.displayed_images = []
        self.image_frames = []

        image_frame = ctk.CTkFrame(master=self.images_frame)

        self.image_frames.append(image_frame)

        image_frame.grid(row=1, column=0, padx=20, pady=20)

        displayed_image = ctk.CTkLabel(
            master=image_frame, text="")

        self.displayed_images.append(displayed_image)

        displayed_image.grid(row=0, column=0, columnspan=2,
                             sticky="ew", padx=10, pady=10)

        image_frame.bind(
            "<MouseWheel>", command=lambda event: self.on_image_scroll(event, 0))
        displayed_image.bind(
            "<MouseWheel>", command=lambda event: self.on_image_scroll(event, 0))

        image_frame.bind(
            "<Button-4>", command=lambda event: self.on_image_scroll_up(0))
        displayed_image.bind(
            "<Button-4>", command=lambda event: self.on_image_scroll_up(0))

        image_frame.bind(
            "<Button-5>", command=lambda event: self.on_image_scroll_down(0))
        displayed_image.bind(
            "<Button-5>", command=lambda event: self.on_image_scroll_down(0))

        displayed_image.bind(
            "<Enter>", command=lambda event: self.set_image_hover_idx(0))

        displayed_image.bind(
            "<Leave>", command=lambda event: self.set_image_hover_idx(-1))

    def display_new_comparison(self):

        self.reset_tab()

        key = self.sort_alg.get_comparison(self.user)

        if key:
            self.progress_bar.grid(
                row=2, column=0, columnspan=2, sticky="N", pady=5)
            # load initial images
            self.images = [[key, self.load_initial_image(key), 0]]
            self.update_images()
            self.root.update()
            self.images = [[key, self.file_2_CTkImage(key), 0]]
            self.update_images()
            self.progress_bar.grid_forget()
            self.progress_bar_progress = 0
        else:
            key = random.sample(self.sort_alg.data, 1)
            self.images = [[key, self.file_2_CTkImage(key), 0]]
            self.update_images()
            IsFinishedPopOut(self.root, self.center,
                             self.back_to_menu, 'no annotations')

    def on_tab(self):

        if self.tab_index >= 0:
            self.remove_highlight(self.tab_items[self.tab_index])

        self.tab_index += 1
        if self.tab_index >= len(self.tab_items):
            self.tab_index = 0

        self.highlight(self.tab_items[self.tab_index])

    def reset_tab(self):
        if self.tab_index != -1:
            self.remove_highlight(self.tab_items[self.tab_index])
            self.tab_index = -1

    def on_shortcmd_up(self, index):

        if index >= len(self.tab_items):
            return

        self.remove_highlight(self.tab_items[index])
        self.root.update()
        self.tab_items[index].invoke()

    def highlight(self, widget):
        widget.configure(fg_color=widget.cget("hover_color"))

    def remove_highlight(self, widget):
        widget.configure(fg_color=['#3a7ebf', '#1f538d'])

    def on_enter(self):
        if self.tab_index >= 0:
            self.tab_items[self.tab_index].invoke()

    def on_shortcmd(self, index):

        if index >= len(self.tab_items):
            return

        self.highlight(self.tab_items[index])

    def submit(self, lvl):

        if self.is_loading:
            return

        key = [key for key, _, _ in self.images][0]

        self.submit_comparison(key, lvl)
