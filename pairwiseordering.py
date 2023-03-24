import copy
import random
import customtkinter as ctk
from helper_functions import DiffLevel
import time
import os
import pandas as pd
from is_finished_pop_out import IsFinishedPopOut
import sorting_algorithms as sa
from utils import *
from ordering import OrderingScreen


class PairwiseOrderingScreen(OrderingScreen):

    def __init__(self, root, save_obj, menu_callback, center, user):

        super().__init__(root, save_obj, menu_callback, center, user)

        self.buttons_frame = ctk.CTkFrame(master=self.root)

        self.question = ctk.CTkLabel(
            master=self.root, text="The bronchial wall thickening on the right looks to be ...", font=('Helvetica bold', 20))

        self.alot_less_button = ctk.CTkButton(master=self.buttons_frame, text="Much Less Severe (1)", width=160,
                                              height=40, command=lambda: self.submit_comparison(-2), font=('Helvetica bold', 20))
        self.less_button = ctk.CTkButton(master=self.buttons_frame, text="Less Severe (2)", width=160,
                                         height=40, command=lambda: self.submit_comparison(-1), font=('Helvetica bold', 20))
        self.same_button = ctk.CTkButton(master=self.buttons_frame, text="Equally Severe (3)", width=160,
                                         height=40, command=lambda: self.submit_comparison(0), font=('Helvetica bold', 20))
        self.more_button = ctk.CTkButton(master=self.buttons_frame, text="More Severe (4)", width=160,
                                         height=40, command=lambda: self.submit_comparison(1), font=('Helvetica bold', 20))
        self.alot_more_button = ctk.CTkButton(master=self.buttons_frame, text="Much More Severe (5)", width=160,
                                              height=40, command=lambda: self.submit_comparison(2), font=('Helvetica bold', 20))

        self.tab_index = -1

        if not type(self.sort_alg) == sa.MergeSort:
            self.tab_items = [self.alot_less_button, self.less_button,
                              self.same_button, self.more_button, self.alot_more_button]
        else:
            self.tab_items = [self.less_button, self.more_button]
            self.less_button.configure(text="Less Severe (1)")
            self.more_button.configure(text="More Severe (2)")

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

        self.root.bind(
            "<Return>", lambda event: self.on_enter())

        self.root.bind(
            "<Tab>", lambda event: self.on_tab())

    def display(self):

        self.session_start_time = time.time()
        self.session_elapsed_time_prev = 0

        self.root.grid_rowconfigure(0, weight=2, uniform="ordering")
        self.root.grid_rowconfigure(1, weight=2, uniform="ordering")
        self.root.grid_rowconfigure(2, weight=12, uniform="ordering")
        self.root.grid_rowconfigure(3, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(4, weight=2, uniform="ordering")
        self.root.grid_rowconfigure(5, weight=4, uniform="ordering")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.images_frame.grid(row=2, column=0, columnspan=2, padx=0, pady=0)

        self.header.grid(row=0, column=0, columnspan=2, sticky="S")

        self.question.grid(row=4, column=0, columnspan=2, pady=10, sticky="S")

        self.buttons_frame.grid(row=5, column=0, columnspan=2, sticky="N")

        if not type(self.sort_alg) == sa.MergeSort:
            self.alot_less_button.grid(row=0, column=0, padx=(10, 5), pady=10)
            self.less_button.grid(row=0, column=1, padx=5, pady=10)
            self.same_button.grid(row=0, column=2, padx=5, pady=10)
            self.more_button.grid(row=0, column=3, padx=5, pady=10)
            self.alot_more_button.grid(row=0, column=4, padx=(5, 10), pady=10)
        else:
            self.less_button.grid(row=0, column=0, padx=(10, 5), pady=10)
            self.more_button.grid(row=0, column=1, padx=(5, 10), pady=10)

        self.session_duration_label.grid(
            row=1, column=1, sticky='SE', padx=100)
        self.comp_count_label.grid(row=1, column=0, sticky='SW', padx=100)

        self.back_button.place(x=20, y=20)

        self.timer_after = self.root.after(1000, self.update_time)

        if not self.is_finished_check():
            self.display_new_comparison()

    def init_image_frames(self):

        self.displayed_images = []
        self.image_frames = []

        for i in range(2):

            image_frame = ctk.CTkFrame(master=self.images_frame)

            self.image_frames.append(image_frame)

            image_frame.grid(row=1, column=i, padx=20, pady=20)

            displayed_image = ctk.CTkLabel(
                master=image_frame, text="")

            self.displayed_images.append(displayed_image)

            displayed_image.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=10)

            image_frame.bind("<MouseWheel>", command=lambda event,
                             i=i: self.on_image_scroll(event, i))
            displayed_image.bind(
                "<MouseWheel>", command=lambda event, i=i: self.on_image_scroll(event, i))

            image_frame.bind("<Button-4>", command=lambda event,
                             i=i: self.on_image_scroll_up(i))
            displayed_image.bind("<Button-4>", command=lambda event,
                             i=i: self.on_image_scroll_up(i))

            image_frame.bind("<Button-5>", command=lambda event,
                             i=i: self.on_image_scroll_down(i))
            displayed_image.bind("<Button-5>", command=lambda event,
                             i=i: self.on_image_scroll_down(i))

    def display_new_comparison(self):

        self.reset_tab()

        keys = self.sort_alg.get_comparison(self.user)

        df_res = self.check_df_for_comp(keys)
        if df_res is not None:
            self.submit_comparison(df_res, df_annotatation=True)
        elif keys:
            self.progress_bar.grid(row=3, column=0, columnspan=2, sticky="N", pady=5)
            self.images = [[img, self.load_initial_image(img), 0] for img in keys] #load initial images
            self.update_images()
            self.root.update()
            self.images = [[img, self.file_2_CTkImage(img), 0] for img in keys]
            self.update_images()
            self.progress_bar.grid_forget()
            self.progress_bar_progress = 0
        else:
            keys = random.sample(self.sort_alg.data, 2)
            self.images = [[img, self.file_2_CTkImage(img), 0] for img in keys]
            self.update_images()
            IsFinishedPopOut(self.root, self.center,
                             self.back_to_menu, 'no annotations')

    def check_df_for_comp(self, keys):

        df_check = pd.read_csv(get_full_path(
            self.save_obj["path_to_save"] + '.csv'))

        a_v_b = df_check.loc[(df_check['result'] == str(keys))
                             & (df_check['undone'] == False)]
        b_v_a = df_check.loc[(df_check['result'] == str(keys[::-1]))
                             & (df_check['undone'] == False)]

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

    def highlight(self, widget):

        hex = widget.cget("fg_color")[1]

        rgb = [int(hex[i:i+2], 16) for i in (1, 3, 5)]
        for i in range(len(rgb)):
            rgb[i] = min(rgb[i]+50, 255)

        new_hex = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
        widget.configure(fg_color=new_hex)

    def remove_highlight(self, widget):
        widget.configure(fg_color=['#3a7ebf', '#1f538d'])

    def on_enter(self):
        self.tab_items[self.tab_index].invoke()

    def on_shortcmd(self, index):
        self.tab_items[index].invoke()

    def submit_comparison(self, difflevel, df_annotatation=False):
        self.reset_tab()
        self.prev_sort_alg = copy.deepcopy(self.sort_alg)

        keys = [key for key, _, _ in self.images]

        if difflevel < 0:
            keys.reverse()

        diff_lvls = [DiffLevel(abs(difflevel))]

        user = 'DF' if df_annotatation else self.user
        self.sort_alg.inference(user, keys, diff_lvls)

        self.save_to_csv_file(keys, diff_lvls, df_annotatation)
        self.comp_count += 1
        self.comp_count_label.configure(
            text=f"Comparison count: {self.comp_count}")

        self.save_algorithm()

        self.session_elapsed_time_prev = time.time() - self.session_start_time

        if not self.is_finished_check():
            self.display_new_comparison()

    def save_to_csv_file(self, keys, diff_lvls, df_annotatation=False):

        user = 'DF' if df_annotatation else self.user
        df = pd.DataFrame({'result': [keys],
                           'diff_levels': [diff_lvls],
                           'time': [time.time()-self.session_start_time],
                           'session': [self.session_id],
                           'user': [user],
                           'undone': [False]})

        output_path = get_full_path(self.save_obj["path_to_save"] + ".csv")
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))
