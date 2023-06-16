import copy
import customtkinter as ctk
from uuid import uuid4
from utils import *
from PIL import Image
import nibabel as nib
import time
import numpy as np
import pickle
from is_finished_pop_out import IsFinishedPopOut
from switching_modes_pop_out import SwitchingModesPopOut
import shutil
import pandas as pd
from pathlib import Path
import sorting_algorithms as sa


class OrderingScreen():

    def __init__(self, root, save_obj, menu_callback, center, user, reload_ordering_screen, hybrid_transition_made):

        self.root = root
        self.menu_callback = menu_callback
        self.center = center
        self.user = user
        self.reload_ordering_screen = reload_ordering_screen

        self.hybrid_transition_made = hybrid_transition_made

        self.save_obj = save_obj
        self.sort_alg = save_obj["sort_alg"]
        self.prev_sort_alg = None
        self.comparison_size = self.sort_alg.comparison_size

        self.images_frame = ctk.CTkFrame(master=self.root)

        self.init_image_frames()

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation", font=('Helvetica bold', 40))

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0:00", font=('Helvetica bold', 30))

        try:
            csv_df = pd.read_csv(get_full_path(
                self.save_obj["path_to_save"] + '.csv'))
        except:
            if type(self.sort_alg) == sa.Rating:
                df = pd.DataFrame(
                    columns=['src', 'rating', 'time', 'session', 'user', 'undone'])
            else:
                df = pd.DataFrame(
                    columns=['result', 'diff_levels', 'time', 'session', 'user', 'undone'])

            df.to_csv(self.save_obj["path_to_save"] + ".csv", index=False)
            csv_df = pd.read_csv(get_full_path(
                self.save_obj["path_to_save"] + '.csv'))

        if self.hybrid_transition_made:
            current_user_count = len(
                csv_df.loc[(csv_df['user'] == self.user) & (csv_df['undone'] == False) & (csv_df['type'] == "Ranking")])
        else:
            current_user_count = len(
                csv_df.loc[(csv_df['user'] == self.user) & (csv_df['undone'] == False)])

        self.comp_count = 0 + current_user_count
        if not type(self.sort_alg) == sa.RatingAlgorithm:
            self.comp_count_label = ctk.CTkLabel(
                master=self.root, text=f"Comparison count: {self.comp_count}/{self.sort_alg.get_comparison_max()}", font=('Helvetica bold', 30))
        else:
            self.comp_count_label = ctk.CTkLabel(
                master=self.root, text=f"Rating count: {self.comp_count}", font=('Helvetica bold', 30))

        self.comparison_bar = ctk.CTkProgressBar(
            self.root, width=400, height=20)
        self.update_comparison_bar()

        self.back_button = ctk.CTkButton(
            master=self.root, text="Back To Menu", width=200, height=40, command=self.back_to_menu, font=('Helvetica bold', 18))

        self.session_id = uuid4()

        self.root.bind("<Control-z>", lambda event: self.undo_annotation())
        self.root.bind("<Control-Z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-z>", lambda event: self.undo_annotation())
        self.root.bind("<Command-Z>", lambda event: self.undo_annotation())

        self.root.bind("<Up>", lambda event: self.on_image_key_scroll('up'))
        self.root.bind(
            "<Down>", lambda event: self.on_image_key_scroll('down'))

        self.progress_bar = ctk.CTkProgressBar(self.root, width=400)
        self.progress_bar_progress = 0
        self.progress_bar.set(0)

        self.undo_label = ctk.CTkLabel(
            master=self.root, text="Undo Last Annotation", font=('Helvetica bold', 20), text_color="#777777")

        self.undo_label.bind(
            "<Enter>", lambda event: self.highlight_label(self.undo_label))
        self.undo_label.bind(
            "<Leave>", lambda event: self.remove_highlight_label(self.undo_label))
        self.undo_label.bind(
            "<Button-1>", lambda event: self.undo_annotation())

        self.is_loading = False
        self.scroll_allowed = save_obj["scroll_allowed"]
        self.submission_timeout = False

    def file_2_CTkImage(self, img_src):

        img_src = get_full_path(img_src)

        _, extension = os.path.splitext(img_src)

        if extension == '.nii':
            ctk_imgs = []
            nib_imgs = nib.load(img_src).get_fdata()

            for i in range(nib_imgs.shape[2]):
                img = nib_imgs[:, :, i]
                resize_factor = (
                    self.root.winfo_screenheight()/2) / img.shape[1]
                new_shape = (
                    int(img.shape[0] * resize_factor), int(img.shape[1] * resize_factor))
                ctk_imgs.append(ctk.CTkImage(
                    Image.fromarray(np.rot90(img)).resize(new_shape, resample=2), size=(new_shape)))
                self.progress_bar_progress += 1
                self.progress_bar.set(
                    self.progress_bar_progress / (self.comparison_size * nib_imgs.shape[2]))
                self.root.update()

            return ctk_imgs
        else:
            return [ctk.CTkImage(Image.open(img_src), size=(250, 250))]

    def highlight_label(self, widget):

        hex = widget.cget("text_color")

        rgb = [int(hex[i:i+2], 16) for i in (1, 3, 5)]
        for i in range(len(rgb)):
            rgb[i] = min(rgb[i]+50, 255)

        new_hex = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
        widget.configure(text_color=new_hex)

    def remove_highlight_label(self, widget):
        widget.configure(text_color="#777777")

    def load_initial_image(self, img_src):
        img_src = get_full_path(img_src)
        _, extension = os.path.splitext(img_src)

        if extension == '.nii':
            ctk_imgs = []
            nib_imgs = nib.load(img_src).get_fdata()

            img = nib_imgs[:, :, 0]
            resize_factor = (self.root.winfo_screenheight()/2) / img.shape[1]
            new_shape = (int(img.shape[0] * resize_factor),
                         int(img.shape[1] * resize_factor))
            ctk_imgs.append(ctk.CTkImage(Image.fromarray(np.rot90(img)).resize(
                new_shape, resample=2), size=(new_shape)))

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

    def on_image_scroll_up(self, idx):
        self.images[idx][2] = min(
            self.images[idx][2]+1, len(self.images[idx][1])-1)

        self.update_images()

    def on_image_scroll_down(self, idx):
        self.images[idx][2] = max(self.images[idx][2]-1, 0)

        self.update_images()

    def on_image_key_scroll(self, dir):
        if self.image_hover_idx >= 0:
            if dir == 'up':
                self.on_image_scroll_up(self.image_hover_idx)
            elif dir == 'down':
                self.on_image_scroll_down(self.image_hover_idx)

    def set_image_hover_idx(self, idx):
        self.image_hover_idx = idx

    def undo_annotation(self):
        if self.prev_sort_alg is not None:

            self.sort_alg = self.prev_sort_alg
            self.save_obj['sort_alg'] = self.prev_sort_alg
            self.prev_sort_alg = None

            self.undo_label.place_forget()

            self.undo_csv_file()
            self.save_algorithm()
            self.display_new_comparison()

            self.comp_count -= 1
            self.comp_count_label.configure(
                text=f"Comparison count: {self.comp_count}/{self.sort_alg.get_comparison_max()}")
            self.update_comparison_bar()

    def update_comparison_bar(self):
        self.comparison_bar.set(
            self.comp_count / self.sort_alg.get_comparison_max())

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

    def submit_comparison(self, keys, lvl, df_annotatation=False):

        if self.submission_timeout:
            return

        self.submission_timeout = True

        self.is_loading = True

        self.prev_sort_alg = copy.deepcopy(self.sort_alg)

        user = 'DF' if df_annotatation else self.user

        self.sort_alg.inference(user, keys, lvl)

        self.save_to_csv_file(keys, lvl, df_annotatation)

        self.comp_count += 1
        self.comp_count_label.configure(
            text=f"Comparison count: {self.comp_count}/{self.sort_alg.get_comparison_max()}")

        if not type(self.sort_alg) == sa.RatingAlgorithm:
            self.comp_count_label.configure(
                text=f"Comparison count: {self.comp_count}/{self.sort_alg.get_comparison_max()}")
        else:
            self.comp_count_label.configure(
                text=f"Rating count: {self.comp_count}/{self.sort_alg.get_comparison_max()}")

        self.update_comparison_bar()

        self.save_algorithm()

        self.session_elapsed_time_prev = time.time() - self.session_start_time

        if not self.is_finished_check():
            if type(self.sort_alg) == sa.HybridTrueSkill and not self.sort_alg.is_rating and not self.hybrid_transition_made:
                self.root.after_cancel(self.timer_after)
                # Switching modes popout
                self.reload_ordering_screen(self.save_obj)
                SwitchingModesPopOut(self.root, self.center)
            else:
                self.display_new_comparison()

        self.is_loading = False
        # Change back to 1000
        self.root.after(100, self.remove_submission_timeout)

    def remove_submission_timeout(self):
        self.submission_timeout = False

    def save_to_csv_file(self, res, lvls, df_annotatation=False):

        user = 'DF' if df_annotatation else self.user

        if isinstance(res, str):
            result = (res, lvls)
            diff_levels = ""
            annotation_type = "Rating"
        else:
            result = res
            diff_levels = lvls
            annotation_type = "Ranking"

        df = pd.DataFrame({'result': [result],
                           'diff_level': [diff_levels],
                           'time': [time.time()-self.session_start_time],
                           'session': [self.session_id],
                           'user': [user],
                           'undone': [False],
                           'type': [annotation_type]})

        output_path = get_full_path(self.save_obj["path_to_save"] + ".csv")
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path), index=False)

    def undo_csv_file(self):
        path = get_full_path(self.save_obj["path_to_save"] + '.csv')
        copy_df = pd.read_csv(path)
        copy_df.iloc[-1, copy_df.columns.get_loc('undone')] = True
        copy_df.to_csv(path, index=False)

    def back_to_menu(self):
        self.root.after_cancel(self.timer_after)
        self.root.unbind("<Return>")
        self.menu_callback()
