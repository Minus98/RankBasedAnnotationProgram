import json
import random
import time
from typing import Callable, List, Optional

import customtkinter as ctk
import pandas as pd

import sorting_algorithms as sa
from is_finished_pop_out import IsFinishedPopOut
from ordering import OrderingScreen
from utils import DiffLevel, get_full_path


class PairwiseOrderingScreen(OrderingScreen):
    """A screen for pairwise image ordering."""

    def __init__(
            self, root: ctk.CTk, save_obj: dict, menu_callback: Callable,
            center: Callable, user: str, reload_ordering_screen: Callable):
        """
        Initialize the PairwiseOrderingScreen.

        Args:
            root (CTk): The root cutom tkinter object.
            save_obj (dict): The save object containing various parameters.
            menu_callback (function): The callback function for the menu.
            center (function): The function for centering the window.
            user (str): The user currently annotating.
            reload_ordering_screen (function): Callback function to reload the 
                                               ordering screen.
        """

        super().__init__(root, save_obj, menu_callback,
                         center, user, reload_ordering_screen, True)

        self.buttons_frame = ctk.CTkFrame(master=self.root)

        with open('prompts.json', 'r') as file:
            prompts = json.load(file)

        ranking_buttons = prompts['ranking_buttons']

        self.alot_less_button = ctk.CTkButton(
            master=self.buttons_frame, text=ranking_buttons[0] + ' (1)',
            width=160, height=40, command=lambda: self.submit(-2),
            font=('Helvetica bold', 20))
        self.less_button = ctk.CTkButton(
            master=self.buttons_frame, text=ranking_buttons[1] + ' (2)',
            width=160, height=40, command=lambda: self.submit(-1),
            font=('Helvetica bold', 20))
        self.same_button = ctk.CTkButton(
            master=self.buttons_frame, text=ranking_buttons[2] + ' (3)',
            width=160, height=40, command=lambda: self.submit(0),
            font=('Helvetica bold', 20))
        self.more_button = ctk.CTkButton(
            master=self.buttons_frame, text=ranking_buttons[3] + ' (4)',
            width=160, height=40, command=lambda: self.submit(1),
            font=('Helvetica bold', 20))
        self.alot_more_button = ctk.CTkButton(
            master=self.buttons_frame, text=ranking_buttons[4] + ' (5)',
            width=160, height=40, command=lambda: self.submit(2),
            font=('Helvetica bold', 20))

        self.tab_index = -1

        if not type(self.sort_alg) == sa.MergeSort:
            self.tab_items = [
                self.alot_less_button, self.less_button, self.same_button,
                self.more_button, self.alot_more_button]
        else:
            self.tab_items = [self.less_button, self.more_button]
            self.less_button.configure(text=ranking_buttons[1] + ' (1)')
            self.more_button.configure(text=ranking_buttons[3] + ' (2)')

        self.root.bind(
            "1", lambda event: self.on_shortcmd(0))
        self.root.bind(
            "2", lambda event: self.on_shortcmd(1))
        self.root.bind(
            "3", lambda event: self.on_shortcmd(2))
        self.root.bind(
            "4", lambda event: self.on_shortcmd(3))
        self.root.bind(
            "5", lambda event: self.on_shortcmd(4))

        self.root.bind("<KeyRelease-1>", lambda event: self.on_shortcmd_up(0))
        self.root.bind("<KeyRelease-2>", lambda event: self.on_shortcmd_up(1))
        self.root.bind("<KeyRelease-3>", lambda event: self.on_shortcmd_up(2))
        self.root.bind("<KeyRelease-4>", lambda event: self.on_shortcmd_up(3))
        self.root.bind("<KeyRelease-5>", lambda event: self.on_shortcmd_up(4))

        self.root.bind(
            "<Return>", lambda event: self.on_enter())

        self.root.bind(
            "<Tab>", lambda event: self.on_tab())

    def display(self):

        self.session_start_time = time.time()
        self.session_elapsed_time_prev = 0

        self.root.grid_rowconfigure(0, weight=3, uniform="ordering")
        self.root.grid_rowconfigure(1, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(2, weight=26, uniform="ordering")
        self.root.grid_rowconfigure(3, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(4, weight=4, uniform="ordering")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        if not self.sort_alg.is_finished():
            self.images_frame.grid(
                row=2, column=0, columnspan=2, padx=0, pady=0)

        self.comparison_bar.grid(row=1, column=0, columnspan=2, pady=(10, 0))

        self.buttons_frame.grid(
            row=4, column=0, columnspan=2, pady=10, sticky="N")

        if not type(self.sort_alg) == sa.MergeSort:
            self.alot_less_button.grid(row=0, column=0, padx=(10, 5), pady=10)
            self.less_button.grid(row=0, column=1, padx=5, pady=10)
            self.same_button.grid(row=0, column=2, padx=5, pady=10)
            self.more_button.grid(row=0, column=3, padx=5, pady=10)
            self.alot_more_button.grid(row=0, column=4, padx=(5, 10), pady=10)
        else:
            self.less_button.grid(row=0, column=0, padx=(10, 5), pady=10)
            self.more_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.session_duration_label.place(relx=0.98, y=20, anchor="ne")

        self.comp_count_label.grid(row=0, column=0, columnspan=2, sticky="S")

        self.back_button.place(x=20, y=20)

        self.timer_after = self.root.after(1000, self.update_time)

        if not self.is_finished_check():
            self.display_new_comparison()

    def init_image_frames(self):
        """
        Display the pairwise ordering screen.
        """

        self.displayed_images = []
        self.image_frames = []

        img_info = {"A": 'sw', "B": 'se'}

        for i in range(2):

            image_frame = ctk.CTkFrame(master=self.images_frame)

            self.image_frames.append(image_frame)

            image_frame.grid(row=1, column=i, padx=20, pady=20)

            displayed_image = ctk.CTkLabel(
                master=image_frame, text="")

            img_name = list(img_info.keys())[i]

            img_label = ctk.CTkLabel(
                master=displayed_image, text=img_name,
                font=('Helvetica bold', 20),
                width=30, height=30, bg_color=image_frame.cget('fg_color'))

            self.displayed_images.append(displayed_image)

            displayed_image.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=10)

            img_label.place(relx=abs(i - 0.01), rely=0.99,
                            anchor=img_info[img_name])

            image_frame.bind("<MouseWheel>", command=lambda event,
                             i=i: self.on_image_scroll(event, i))
            displayed_image.bind(
                "<MouseWheel>", command=lambda event,
                i=i: self.on_image_scroll(event, i))

            image_frame.bind("<Button-4>", command=lambda event,
                             i=i: self.on_image_scroll_up(i))
            displayed_image.bind("<Button-4>", command=lambda event,
                                 i=i: self.on_image_scroll_up(i))

            image_frame.bind("<Button-5>", command=lambda event,
                             i=i: self.on_image_scroll_down(i))
            displayed_image.bind("<Button-5>", command=lambda event,
                                 i=i: self.on_image_scroll_down(i))

            displayed_image.bind(
                "<Enter>", command=lambda event,
                i=i: self.set_image_hover_idx(i))

            displayed_image.bind(
                "<Leave>", command=lambda event: self.set_image_hover_idx(-1))

    def display_new_comparison(self):
        """
        Display a new comparison in the pairwise ordering screen.
        """

        self.reset_tab()

        keys = self.sort_alg.get_comparison(self.user)

        df_res = self.check_df_for_comp(keys)
        if df_res is not None:
            self.submit(df_res, df_annotatation=True)
        elif keys:
            self.images = [[img, self.load_initial_image(
                img), 0] for img in keys]  # load initial images
            self.update_images()
            self.root.update()
            if self.scroll_allowed:
                self.progress_bar.grid(
                    row=3, column=0, columnspan=2, sticky="N", pady=5)
                self.images = [
                    [img, self.file_2_CTkImage(img), 0] for img in keys]
                self.update_images()
                self.progress_bar.grid_forget()
                self.progress_bar_progress = 0

            if self.prev_sort_alg is not None:
                self.undo_label.place(x=20, y=70)
        else:
            keys = random.sample(self.sort_alg.data, 2)
            self.images = [[img, self.file_2_CTkImage(img), 0] for img in keys]
            self.update_images()
            IsFinishedPopOut(self.root, self.center,
                             self.back_to_menu, 'no annotations')

    def check_df_for_comp(self, keys: List[str]) -> Optional[int]:
        """
        Check the data frame for previous comparisons and if they are 
        enough and sufficient. 

        Args:
            keys (List[str]): The keys representing the current comparison.

        Returns:
            Optional[int]: The result of the comparison where 70% of users 
                           assess the same difference level 
                           0 - if consensus is no difference
                           1 or -1 - if consensus is that there is some order 
                           of the keys or None if not enough previous comparison are 
                           found.
        """
        df_check = pd.read_csv(get_full_path(
            self.save_obj["path_to_save"] + '.csv'))

        a_v_b = df_check.loc[(df_check['result'] == str(keys))
                             & (~df_check['undone'])]

        b_v_a = df_check.loc[(df_check['result'] == str(keys[::-1]))
                             & (~df_check['undone'])]

        a_v_b_draw = a_v_b.loc[a_v_b['diff_levels'] == str([DiffLevel(0)])]
        a_v_b_win = a_v_b.loc[a_v_b['diff_levels'] != str([DiffLevel(0)])]

        b_v_a_draw = b_v_a.loc[b_v_a['diff_levels'] == str([DiffLevel(0)])]
        b_v_a_win = b_v_a.loc[b_v_a['diff_levels'] != str([DiffLevel(0)])]

        n = len(a_v_b) + len(b_v_a)

        if n > 2:
            if len(a_v_b_draw) + len(b_v_a_draw) / n > .7:
                return 0
            elif len(a_v_b_win) / n > .7:
                return 1
            elif len(b_v_a_win) / n > .7:
                return -1
        return None

    def on_tab(self):
        """
        Perform an action when the tab key is pressed.
        """

        if self.tab_index >= 0:
            self.remove_highlight(self.tab_items[self.tab_index])

        self.tab_index += 1
        if self.tab_index >= len(self.tab_items):
            self.tab_index = 0

        self.highlight(self.tab_items[self.tab_index])

    def reset_tab(self):
        """
        Reset the tab index and remove the highlight from the current tab item.
        """
        if self.tab_index != -1:
            self.remove_highlight(self.tab_items[self.tab_index])
            self.tab_index = -1

    def highlight(self, widget):
        """
        Highlight the specified widget.

        Args:
            widget: The widget to highlight.
        """
        widget.configure(fg_color=widget.cget("hover_color"))

    def remove_highlight(self, widget):
        """
        Remove the highlight from the specified widget.

        Args:
            widget: The widget to remove the highlight from.
        """
        widget.configure(fg_color=['#3a7ebf', '#1f538d'])

    def on_enter(self):
        """
        Perform an action when the enter key is pressed.
        """
        if self.tab_index >= 0:
            self.tab_items[self.tab_index].invoke()

    def on_shortcmd(self, index: int):
        """
        Perform an action when a short command key is pressed.

        Args:
            index (int): The index of the short command key.
        """

        if index >= len(self.tab_items):
            return

        self.highlight(self.tab_items[index])

    def on_shortcmd_up(self, index: int):
        """
        Perform an action when a short command key is released.

        Args:
            index (int): The index of the short command key.
        """

        if index >= len(self.tab_items):
            return

        self.remove_highlight(self.tab_items[index])
        self.root.update()
        self.tab_items[index].invoke()

    def submit(self, difflevel: int, df_annotatation: bool = False):
        """
        Submit a comparison.

        Args:
            difflevel (int): The difference level of the comparison.
            df_annotatation (bool, optional): Whether to annotate the comparison
                                              in the data frame. Defaults to 
                                              False.
        """

        if self.is_loading:
            return

        keys = [key for key, _, _ in self.images]

        if difflevel < 0:
            keys.reverse()

        diff_lvls = [DiffLevel(abs(difflevel))]

        self.submit_comparison(keys, diff_lvls, df_annotatation)
