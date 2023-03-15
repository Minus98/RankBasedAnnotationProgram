import copy
from pathlib import Path
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
from utils import *


class OrderingScreen():

    def __init__(self, root, save_obj, menu_callback, center, user):

        self.root = root
        self.menu_callback = menu_callback
        self.center = center
        self.user = user

        self.save_obj = save_obj
        self.sort_alg = save_obj["sort_alg"]
        self.prev_sort_alg = None
        self.comparison_size = self.sort_alg.comparison_size

        self.images_frame = ctk.CTkFrame(master=self.root)

        self.init_image_frames()

        self.int_diff_levels = [ctk.IntVar(None, 1)
                                for _ in range(self.comparison_size - 1)]

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation", font=('Helvetica bold', 40))

        self.submit_button = ctk.CTkButton(
            master=self.root, text="Submit Ordering", width=280, height=60, command=self.submit_comparison, font=('Helvetica bold', 20))

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0:00", font=('Helvetica bold', 30))

        self.comp_count = 0
        self.comp_count_label = ctk.CTkLabel(
            master=self.root, text=f"Comparison count: {self.comp_count}", font=('Helvetica bold', 30))

        self.back_button = ctk.CTkButton(
            master=self.root, text="Back To Menu", width=200, height=40, command=self.back_to_menu, font=('Helvetica bold', 18))

        self.root.bind("<Control-z>", lambda event: self.undo_annotation())
        self.root.bind("<Control-Z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-Z>", lambda event: self.undo_annotation())

        self.motion_allowed = True

        self.session_id = uuid4()

    def display(self):

        self.session_start_time = time.time()
        self.session_elapsed_time_prev = 0

        self.root.grid_rowconfigure(0, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(1, weight=1, uniform="ordering")
        self.root.grid_rowconfigure(2, weight=6, uniform="ordering")
        self.root.grid_rowconfigure(3, weight=1, uniform="ordering")
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        self.images_frame.grid(row=2, column=0, columnspan=2, padx=0, pady=0)

        self.header.grid(row=0, column=0, columnspan=2, sticky="S")
        self.submit_button.grid(row=3, column=0, columnspan=2, sticky="N")
        self.session_duration_label.grid(
            row=1, column=1, sticky='SE', padx=100)
        self.comp_count_label.grid(row=1, column=0, sticky='SW', padx=100)

        self.back_button.place(x=20, y=20)

        self.timer_after = self.root.after(1000, self.update_time)

        if not self.is_finished_check():
            self.display_new_comparison()
            self.init_diff_level_buttons()

    def init_image_frames(self):

        self.displayed_images = []
        self.image_frames = []

        for i in range(self.comparison_size):

            image_frame = ctk.CTkFrame(master=self.images_frame)

            self.image_frames.append(image_frame)

            image_frame.grid(row=1, column=i, padx=20, pady=(5, 20))

            displayed_image = ctk.CTkLabel(
                master=image_frame, text="")

            self.displayed_images.append(displayed_image)

            displayed_image.grid(row=0, column=0, columnspan=2,
                                 sticky="ew", padx=10, pady=10)

            left_button_state = ctk.NORMAL if i != 0 else ctk.DISABLED

            move_left_button = ctk.CTkButton(
                master=image_frame, text="<", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_left(i), state=left_button_state)
            move_left_button.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

            right_button_state = ctk.NORMAL if i != self.comparison_size - 1 else ctk.DISABLED

            move_right_button = ctk.CTkButton(
                master=image_frame, text=">", width=120, height=36, font=('Helvetica bold', 20), command=lambda i=i: self.move_right(i), state=right_button_state)
            move_right_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

            image_frame.bind("<Button-1>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_start(event, image_frame, i))
            image_frame.bind("<B1-Motion>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_motion(event, image_frame, i))
            image_frame.bind("<ButtonRelease-1>", command=lambda event, image_frame=image_frame,
                             i=i: self.on_drag_stop(event, image_frame, i))
            image_frame.bind("<MouseWheel>", command=lambda event,
                             i=i: self.on_image_scroll(event, i))

            displayed_image.bind("<Button-1>", command=lambda event,
                                 image_frame=image_frame, i=i: self.on_drag_start(event, image_frame, i))
            displayed_image.bind("<B1-Motion>", command=lambda event, image_frame=image_frame,
                                 i=i: self.on_drag_motion(event, image_frame, i))
            displayed_image.bind("<ButtonRelease-1>", command=lambda event, image_frame=image_frame,
                                 i=i: self.on_drag_stop(event, image_frame, i))
            displayed_image.bind(
                "<MouseWheel>", command=lambda event, i=i: self.on_image_scroll(event, i))

            self.root.bind(
                "<Return>", lambda event: self.submit_comparison())

    def init_diff_level_buttons(self):

        diff_levels_frame = ctk.CTkFrame(
            master=self.images_frame)

        image_width = self.images[0][1][0]._size[0]

        diff_levels_frame.grid(
            row=0, column=0, columnspan=self.comparison_size, padx=(30 + image_width // 2), pady=(10, 0), sticky="ew")

        for i in range(len(self.int_diff_levels)):
            diff_levels_frame.columnconfigure(i, weight=1)

        for i, int_diff_level in enumerate(self.int_diff_levels):

            diff_level_frame = ctk.CTkFrame(
                master=diff_levels_frame)

            diff_level_frame.grid(row=0, column=i)

            r0 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=0, width=22, text="")
            r1 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=1, width=22, text="")
            r2 = ctk.CTkRadioButton(
                master=diff_level_frame, variable=int_diff_level, value=2, width=22, text="")

            r0.grid(row=1, column=0, padx=(12, 5), pady=2,
                    sticky="ew")
            r1.grid(row=1, column=1, padx=(12, 5), pady=2,
                    sticky="ew")
            r2.grid(row=1, column=2, padx=(12, 5), pady=2,
                    sticky="ew")

            diff_level_label = ctk.CTkLabel(
                text="", master=diff_level_frame, font=('Helvetica bold', 18))
            diff_level_label.grid(row=0, column=0, columnspan=3)

            int_diff_level.trace('w', lambda var, index, mode, int_diff_level=int_diff_level,
                                 label=diff_level_label: self.update_diff_labels(int_diff_level, label))

        diff_levels_frame.configure(
            fg_color=self.images_frame.cget("fg_color"))

    def reset_diff_levels(self):
        for int_diff_lvl in self.int_diff_levels:
            int_diff_lvl.set(1)

    def update_diff_labels(self, int_diff_level, label):
        if int_diff_level.get() == 0:
            label.configure(text="no difference")
        elif int_diff_level.get() == 2:
            label.configure(text="large difference")
        else:
            label.configure(text="")

    def create_image_widget(self, image_idx):
        image_frame = ctk.CTkFrame(
            master=self.root)

        img = self.displayed_images[image_idx].cget("image")

        displayed_image = ctk.CTkLabel(
            master=image_frame, text="", image=img)

        displayed_image.grid(row=0, column=0, columnspan=2,
                             sticky="ew", padx=10, pady=10)

        move_left_button = ctk.CTkButton(
            master=image_frame, text="<", width=120, height=36, font=('Helvetica bold', 20), state=ctk.DISABLED)
        move_left_button.grid(row=1, column=0, padx=(5, 0), pady=(0, 10))

        move_right_button = ctk.CTkButton(
            master=image_frame, text=">", width=120, height=36, font=('Helvetica bold', 20), state=ctk.DISABLED)
        move_right_button.grid(row=1, column=1, padx=(0, 5), pady=(0, 10))

        return image_frame

    def display_new_comparison(self):
        keys = self.sort_alg.get_comparison("1")
        self.images = [[img, self.file_2_CTkImage(img), 0]
                       for img in keys]
        self.update_images()

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

    def move_left(self, index):

        if index > 0:
            self.images[index], self.images[index -
                                            1] = self.images[index - 1], self.images[index]

        self.update_images()

        self.reset_diff_levels()

    def move_right(self, index):

        if index < len(self.images) - 1:
            self.images[index], self.images[index +
                                            1] = self.images[index + 1], self.images[index]

        self.update_images()

        self.reset_diff_levels()

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

    def on_drag_start(self, event, frame, idx):

        self.black_frame = ctk.CTkFrame(master=self.images_frame, width=frame.winfo_width(
        ), height=frame.winfo_height())

        self.black_frame.place(x=frame.winfo_x(), y=frame.winfo_y())

        pos_x = self.images_frame.winfo_x() + frame.winfo_x() + event.x
        pos_y = self.images_frame.winfo_y() + frame.winfo_y() + event.y

        dx = frame.winfo_width()//2
        dy = frame.winfo_height()//2

        frame_clone = self.create_image_widget(idx)
        frame_clone.place(x=pos_x-dx, y=pos_y-dy)

        self.drag_frame = frame_clone

    def allow_motion(self):
        self.motion_allowed = True

    def on_drag_motion(self, event, frame, idx):

        if not self.motion_allowed:
            return
        else:
            self.motion_allowed = False
            self.root.after(10, self.allow_motion)

        x = self.images_frame.winfo_x() + frame.winfo_x() + event.x - \
            self.drag_frame.winfo_width()//2

        y = self.images_frame.winfo_y() + frame.winfo_y() + event.y - \
            self.drag_frame.winfo_height()//2

        self.drag_frame.place(x=x, y=y)

        self.root.update_idletasks()

    def on_drag_stop(self, event, frame, idx):

        self.drag_frame.place_forget()
        self.black_frame.place_forget()

        index, row = self.images_frame.grid_location(
            frame.winfo_x() + event.x, event.y)

        if row != 1 or index < 0 or index >= len(self.images) or index == idx:
            return

        widget = self.image_frames[index]

        width = widget.winfo_width()

        # Change 20 to get padx of images_frame
        relative_x = frame.winfo_x() + event.x - widget.winfo_x() + 20

        from_right_bonus = 0

        if (idx > index):
            from_right_bonus = 1

        image_to_move = self.images.pop(idx)
        if relative_x < width // 3:
            self.images.insert(index - 1 + from_right_bonus, image_to_move)
        elif relative_x < 2*width // 3:
            # If you are coming from above, same as lower third
            # If you are coming from below, same as upper third
            if from_right_bonus:
                self.images.insert(index - 1 + from_right_bonus, image_to_move)
            else:
                self.images.insert(index + from_right_bonus, image_to_move)
        else:
            self.images.insert(index + from_right_bonus, image_to_move)

        self.update_images()
        self.reset_diff_levels()

    # perhaps use "<Button-4> defines the scroll up event on mice with wheel support and and <Button-5> the scroll down." for linux
    def on_image_scroll(self, event, idx):

        if event.delta < 0:
            self.images[idx][2] = max(self.images[idx][2]-1, 0)

        elif event.delta > 0:
            self.images[idx][2] = min(
                self.images[idx][2]+1, len(self.images[idx][1])-1)

        self.update_images()

    def undo_annotation(self):
        if self.prev_sort_alg is not None:

            self.sort_alg = self.prev_sort_alg
            self.save_obj['sort_alg'] = self.prev_sort_alg
            self.prev_sort_alg = None

            self.undo_csv_file()
            self.save_algorithm()
            self.display_new_comparison()

            self.comp_count -= 1
            self.comp_count_label.configure(
                text=f"Comparison count: {self.comp_count}")

    def submit_comparison(self):

        self.prev_sort_alg = copy.deepcopy(self.sort_alg)

        keys = [key for key, _, _ in self.images]

        diff_lvls = [DiffLevel(int_diff_lvl.get())
                     for int_diff_lvl in self.int_diff_levels]

        self.sort_alg.inference("1", keys, diff_lvls)

        self.save_algorithm()

        self.save_to_csv_file(keys, diff_lvls)

        self.comp_count += 1
        self.comp_count_label.configure(
            text=f"Comparison count: {self.comp_count}")

        self.session_elapsed_time_prev = time.time() - self.session_start_time

        if not self.is_finished_check():
            self.display_new_comparison()

        self.reset_diff_levels()

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
            path = get_full_path(str(Path(src).parent))
            _, extension = os.path.splitext(src)
            new_name = str(i) + extension
            dst = path + '/sorted/' + new_name
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)

    def back_to_menu(self):
        self.root.after_cancel(self.timer_after)
        self.root.unbind("<Return>")
        self.menu_callback()

    def undo_csv_file(self):
        path = get_full_path(self.save_obj["path_to_save"] + '.csv')
        copy_df = pd.read_csv(path)
        copy_df.iloc[-1, copy_df.columns.get_loc('undone')] = True
        copy_df.to_csv(path, index=False)

    def save_to_csv_file(self, keys, diff_lvls):
        df = pd.DataFrame({'result': [keys],
                           'diff_levels': [diff_lvls],
                           'time': [time.time() - self.session_start_time],
                           'session': [self.session_id],
                           'user': [self.user],
                           'undone': [False]})

        output_path = get_full_path(self.save_obj["path_to_save"] + ".csv")
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path))
