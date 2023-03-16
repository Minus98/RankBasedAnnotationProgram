import copy
from pathlib import Path
import random
import customtkinter as ctk
import numpy as np
from helper_functions import DiffLevel
import time
import pickle
import os
from PIL import Image
from tkinter import PhotoImage
import pandas as pd
from is_finished_pop_out import IsFinishedPopOut
from uuid import uuid4
import shutil
import nibabel as nib
import sorting_algorithms as sa
from utils import *


class PairwiseOrderingScreen():

    def __init__(self, root, save_obj, menu_callback, center, user):

        self.root = root
        self.menu_callback = menu_callback
        self.center = center
        self.user = user

        self.save_obj = save_obj
        self.sort_alg = save_obj["sort_alg"]
        self.prev_sort_alg = None

        self.images_frame = ctk.CTkFrame(master=self.root)
        self.buttons_frame = ctk.CTkFrame(master=self.root)

        self.init_image_frames()

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation", font=('Helvetica bold', 40))

        self.question = ctk.CTkLabel(
            master=self.root, text="The person on the right looks to be ...", font=('Helvetica bold', 20))

        self.alot_less_button = ctk.CTkButton(master=self.buttons_frame, text="Much younger (1)", width=160,
                                              height=40, command=lambda: self.submit_comparison(-2), font=('Helvetica bold', 20))
        self.less_button = ctk.CTkButton(master=self.buttons_frame, text="Younger (2)", width=160,
                                         height=40, command=lambda: self.submit_comparison(-1), font=('Helvetica bold', 20))
        self.same_button = ctk.CTkButton(master=self.buttons_frame, text="Of similar age (3)", width=160,
                                         height=40, command=lambda: self.submit_comparison(0), font=('Helvetica bold', 20))
        self.more_button = ctk.CTkButton(master=self.buttons_frame, text="Older (4)", width=160,
                                         height=40, command=lambda: self.submit_comparison(1), font=('Helvetica bold', 20))
        self.alot_more_button = ctk.CTkButton(master=self.buttons_frame, text="Much older (5)", width=160,
                                              height=40, command=lambda: self.submit_comparison(2), font=('Helvetica bold', 20))

        self.tab_index = -1

        if not type(self.sort_alg) == sa.MergeSort:
            self.tab_items = [self.alot_less_button, self.less_button,
                              self.same_button, self.more_button, self.alot_more_button]
        else:
            self.tab_items = [self.less_button, self.more_button]
            self.less_button.configure(text="Younger (1)")
            self.more_button.configure(text="Older (2)")

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

        self.root.bind("<Control-z>", lambda event: self.undo_annotation())
        self.root.bind("<Control-Z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-Z>", lambda event: self.undo_annotation())

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0:00", font=('Helvetica bold', 30))

        csv_df = pd.read_csv(get_full_path(
            self.save_obj["path_to_save"] + '.csv'))
        current_user_count = len(csv_df.loc[csv_df['user'] == self.user])

        self.comp_count = 0 + current_user_count
        self.comp_count_label = ctk.CTkLabel(
            master=self.root, text=f"Your comparison count: {self.comp_count}", font=('Helvetica bold', 30))

        self.back_button = ctk.CTkButton(
            master=self.root, text="Back To Menu", width=200, height=40, command=self.back_to_menu, font=('Helvetica bold', 18))

        self.motion_allowed = True

        self.session_id = uuid4()

    def display(self):

        self.session_start_time = time.time()
        self.session_elapsed_time_prev = 0

        self.root.grid_rowconfigure(0, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(1, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(2, weight=6, uniform="ordering")
        self.root.grid_rowconfigure(3, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(4, weight=2, uniform="ordering")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.images_frame.grid(row=2, column=0, columnspan=2, padx=0, pady=0)

        self.header.grid(row=0, column=0, columnspan=2, sticky="S")

        self.question.grid(row=3, column=0, columnspan=2, pady=10, sticky="S")

        self.buttons_frame.grid(row=4, column=0, columnspan=2, sticky="N")

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

    def display_new_comparison(self):
        keys = self.sort_alg.get_comparison(self.user)

        df_res = self.check_df_for_comp(keys)
        if df_res is not None:
            self.submit_comparison(df_res, df_annotatation=True)
        elif keys:
            self.images = [[img, self.file_2_CTkImage(img), 0] for img in keys]
            self.update_images()
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

    def file_2_CTkImage(self, img_src):

        img_src = get_full_path(img_src)

        _, extension = os.path.splitext(img_src)

        if extension == '.nii':
            ctk_imgs = []
            nib_imgs = nib.load(img_src).get_fdata() + 1024
            nib_imgs = (nib_imgs / np.max(nib_imgs)) * 255

            for i in range(0, nib_imgs.shape[2], 10):
                img = nib_imgs[:, :, i]
                sz = img.shape
                ctk_imgs.append(ctk.CTkImage(Image.fromarray(img), size=sz))

            return ctk_imgs
        else:
            return [ctk.CTkImage(Image.open(img_src), size=(250, 250))]

    def update_images(self):

        for i, img_info in enumerate(self.images):
            self.displayed_images[i].configure(
                image=img_info[1][img_info[2]])

    def update_time(self):

        current_time = time.time()

        elapsed = int(current_time - self.session_start_time)
        (min, sec) = divmod(elapsed, 60)
        (hours, min) = divmod(min, 60)

        if hours:
            text_input = '{:02}:{:02}:{:02}'.format(
                int(hours), int(min), int(sec))
        elif min < 10:
            text_input = '{:01}:{:02}'.format(int(min), int(sec))
        else:
            text_input = '{:02}:{:02}'.format(int(min), int(sec))

        self.session_duration_label.configure(text=text_input)

        self.timer_after = self.root.after(1000, self.update_time)

    # perhaps use "<Button-4> defines the scroll up event on mice with wheel support and and <Button-5> the scroll down." for linux
    def on_image_scroll(self, event, idx):

        if event.delta < 0:
            self.images[idx][2] = max(self.images[idx][2]-1, 0)

        elif event.delta > 0:
            self.images[idx][2] = min(
                self.images[idx][2]+1, len(self.images[idx][1])-1)

        self.update_images()

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

    def undo_annotation(self):
        if self.prev_sort_alg is not None:
            self.reset_tab()

            self.sort_alg = self.prev_sort_alg
            self.save_obj['sort_alg'] = self.prev_sort_alg
            self.prev_sort_alg = None

            self.undo_csv_file()
            self.save_algorithm()
            self.display_new_comparison()

            self.comp_count -= 1
            self.comp_count_label.configure(
                text=f"Comparison count: {self.comp_count}")

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

    def save_algorithm(self):
        f = open(get_full_path(
            self.save_obj["path_to_save"] + ".pickle"), "wb")
        pickle.dump(self.save_obj, f)
        f.close()

    def is_finished_check(self):
        if self.sort_alg.is_finished():
            self.save_sorted_images()
            IsFinishedPopOut(self.root, self.center, self.back_to_menu)
            return True
        return False

    def save_sorted_images(self):
        res = self.sort_alg.get_result()
        for i, src in enumerate(res):
            path = str(Path(get_full_path(src)).parent)
            _, extension = os.path.splitext(src)
            new_name = str(i) + extension
            dst = path + '/sorted/' + new_name
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(get_full_path(src), dst)

    def back_to_menu(self):
        self.root.after_cancel(self.timer_after)
        self.menu_callback()

    def undo_csv_file(self):

        path = get_full_path(
            self.save_obj["path_to_save"] + '.csv')
        copy_df = pd.read_csv(path)
        copy_df.iloc[-1, copy_df.columns.get_loc('undone')] = True
        copy_df.to_csv(path, index=False)

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
