import copy
import os
import shutil
import time
from tkinter import Event
from typing import Callable, List, Union
from uuid import uuid4

import customtkinter as ctk
import nibabel as nib
import numpy as np
import pandas as pd
from PIL import Image

import sorting_algorithms as sa
import utils.convergence as conv
import utils.ctk_utils as ctk_utils
import utils.saves_handler as saves_handler
from pop_outs.image_directory_pop_out import ImageDirectoryPopOut
from pop_outs.is_finished_pop_out import IsFinishedPopOut
from pop_outs.switching_modes_pop_out import SwitchingModesPopOut


class OrderingScreen():
    """Class representing the ordering screen for ranking and rating images."""

    def __init__(
            self, root: ctk.CTk, save_obj: dict, menu_callback: Callable,
            user: str, reload_ordering_screen: Callable,
            hybrid_transition_made: bool, root_bind_callback: Callable):
        """
        Initialize the OrderingScreen.

        Args:
            root (CTk): The root cutom tkinter object.
            save_obj (dict): The save object containing various parameters.
            menu_callback (function): The callback function for the menu.
            user (str): The user currently annotating.
            reload_ordering_screen (function): Callback function to reload the 
                                               ordering screen.
            hybrid_transition_made (bool): Flag indicating whether hybrid 
                                           transition was made.
            root_bind_callback (function): Callback function used to bind events to the
                                           root element.
        """

        self.image_directory_located = False

        self.root = root
        self.menu_callback = menu_callback
        self.user = user
        self.reload_ordering_screen = reload_ordering_screen
        self.root_bind_callback = root_bind_callback

        self.hybrid_transition_made = hybrid_transition_made

        self.save_obj = save_obj
        self.sort_alg = save_obj["sort_alg"]
        self.prev_sort_alg = None
        self.comparison_size = self.sort_alg.comparison_size

        self.images_frame = ctk.CTkFrame(master=self.root)

        self.init_image_frames()

        self.header = ctk.CTkLabel(
            master=self.root, text="Rank-Based Annotation",
            font=('Helvetica bold', 40))

        self.session_duration_label = ctk.CTkLabel(
            master=self.root, text="0:00", font=('Helvetica bold', 30))

        try:
            csv_df = pd.read_csv(saves_handler.get_path_to_save(
                self.save_obj) + '.csv')
        except Exception:

            df = pd.DataFrame(
                columns=['result', 'diff_levels', 'time', 'session', 'user',
                         'undone', 'type'])

            df.to_csv(saves_handler.get_path_to_save(
                self.save_obj) + ".csv", index=False)
            csv_df = pd.read_csv(saves_handler.get_path_to_save(
                self.save_obj) + '.csv')

        if (type(self.sort_alg) == sa.HybridTrueSkill
                and self.hybrid_transition_made):

            current_user_count = len(
                csv_df.loc
                [(~csv_df['undone']) & (csv_df['type'] == "Ranking")])

        elif type(self.sort_alg) == sa.HybridTrueSkill:

            current_user_count = len(
                csv_df.loc[(~csv_df['undone'])])

        else:

            current_user_count = len(
                csv_df.loc
                [(csv_df['user'] == self.user) & (~csv_df['undone'])])

        self.comp_count = 0 + current_user_count
        if not type(self.sort_alg) == sa.RatingAlgorithm:
            self.comp_count_label = ctk.CTkLabel(
                master=self.root,
                text='Comparison count: ' + str(self.comp_count) +
                '/' + str(self.sort_alg.get_comparison_max()),
                font=('Helvetica bold', 30))
        else:
            self.comp_count_label = ctk.CTkLabel(
                master=self.root,
                text='Rating count: ' + str(self.comp_count) +
                '/' + str(self.sort_alg.get_comparison_max()),
                font=('Helvetica bold', 30))

        self.comparison_bar = ctk.CTkProgressBar(
            self.root, width=400, height=20)
        self.update_comparison_bar()

        self.back_button = ctk.CTkButton(
            master=self.root, text="Back To Menu", width=200, height=40,
            command=self.back_to_menu, font=('Helvetica bold', 18))

        self.session_id = uuid4()

        self.root_bind_callback(
            "<Control-z>", lambda event: self.undo_annotation())
        self.root_bind_callback(
            "<Control-Z>", lambda event: self.undo_annotation())
        self.root_bind_callback(
            "<Command-z>", lambda event: self.undo_annotation())
        self.root_bind_callback(
            "<Command-Z>", lambda event: self.undo_annotation())

        self.root_bind_callback(
            "<Up>", lambda event: self.on_image_key_scroll('up'))
        self.root_bind_callback(
            "<Down>", lambda event: self.on_image_key_scroll('down'))

        self.progress_bar = ctk.CTkProgressBar(self.root, width=400)
        self.progress_bar_progress = 0
        self.progress_bar.set(0)

        self.undo_label = ctk.CTkLabel(
            master=self.root, text="Undo Last Annotation",
            font=('Helvetica bold', 20),
            text_color="#777777")

        self.undo_label.bind(
            "<Enter>", lambda event: ctk_utils.highlight_label(
                self.undo_label))
        self.undo_label.bind(
            "<Leave>", lambda event: ctk_utils.remove_highlight_label(
                self.undo_label))
        self.undo_label.bind(
            "<Button-1>", lambda event: self.undo_annotation())

        self.is_loading = False
        self.scroll_allowed = save_obj["scroll_allowed"]
        self.submission_timeout = False

        directory_dict = self.save_obj['user_directory_dict']
        full_img_dir_path = saves_handler.get_full_path(
            self.save_obj['image_directory'])

        if self.user in directory_dict and all(
            [os.path.isfile(directory_dict[self.user] + "/" + k)
             for k in self.sort_alg.data]):
            self.image_directory = directory_dict[self.user]
            self.image_directory_located = True

        elif all([os.path.isfile(full_img_dir_path + "/" + k)
                  for k in self.sort_alg.data]):

            directory_dict[self.user] = full_img_dir_path
            self.image_directory = full_img_dir_path
            self.image_directory_located = True

        else:
            ImageDirectoryPopOut(
                self.root, self.save_obj,
                self.submit_path, self.back_to_menu)

    def file_2_CTkImage(self, img_src: str) -> List[ctk.CTkImage]:
        """
        Convert an image file to a list of CTkImage objects.

        Args:
            img_src (str): The path to the image file.

        Returns:
            List[CTkImage]: The list of CTkImage objects.

        Raises:
            FileNotFoundError: If the image file is not found.
        """

        img_src = self.image_directory + "/" + img_src
        _, extension = os.path.splitext(img_src)

        if extension == '.nii':
            ctk_imgs = []
            nib_imgs = nib.load(img_src).get_fdata()

            for i in range(nib_imgs.shape[2]):
                img = nib_imgs[:, :, i]
                resize_factor = (
                    self.root.winfo_screenheight()/2) / img.shape[1]
                new_shape = (
                    int(img.shape[0] * resize_factor),
                    int(img.shape[1] * resize_factor))
                ctk_imgs.append(
                    ctk.CTkImage(
                        Image.fromarray(np.rot90(img)).resize(
                            new_shape, resample=2),
                        size=(new_shape)))
                self.progress_bar_progress += 1
                self.progress_bar.set(
                    self.progress_bar_progress /
                    (self.comparison_size * nib_imgs.shape[2]))
                self.root.update()

            return ctk_imgs
        else:
            return [ctk.CTkImage(Image.open(img_src), size=(250, 250))]

    def load_initial_image(self, img_src: str) -> List[ctk.CTkImage]:
        """
        Load the initial image for display.

        Args:
            img_src (str): The source of the image file to load.

        Returns:
            A list of CTkImage objects representing the loaded image.
        """

        img_src = self.image_directory + "/" + img_src
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
        """
        Update the displayed images on the screen.
        """

        for i, img_info in enumerate(self.images):
            self.displayed_images[i].configure(
                image=img_info[1][img_info[2]])

    def update_time(self):
        """
        Update the displayed session duration time.
        """

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

    def on_image_scroll(self, event: Event, idx: int):
        """
        Handle the image scroll event.

        Args:
            event (Event): The tkinter scroll event.
            idx (int): The index of the image.
        """
        if event.delta < 0:
            self.images[idx][2] = max(self.images[idx][2]-1, 0)

        elif event.delta > 0:
            self.images[idx][2] = min(
                self.images[idx][2]+1, len(self.images[idx][1])-1)

        self.update_images()

    def on_image_scroll_up(self, idx: int):
        """
        Handle the upward image scroll event.

        Args:
            idx (int): The index of the image.
        """

        self.images[idx][2] = min(
            self.images[idx][2]+1, len(self.images[idx][1])-1)

        self.update_images()

    def on_image_scroll_down(self, idx: int):
        """
        Handle the downward image scroll event.

        Args:
            idx (int): The index of the image.
        """
        self.images[idx][2] = max(self.images[idx][2]-1, 0)

        self.update_images()

    def on_image_key_scroll(self, dir: str):
        """
        Handle the image scroll event triggered by a key press.

        Args:
            dir (str): The direction of the scroll ('up' or 'down').
        """
        if self.image_hover_idx >= 0:
            if dir == 'up':
                self.on_image_scroll_up(self.image_hover_idx)
            elif dir == 'down':
                self.on_image_scroll_down(self.image_hover_idx)

    def set_image_hover_idx(self, idx: int):
        """
        Set the index of the image being hovered.

        Args:
            idx (int): The index of the image.
        """
        self.image_hover_idx = idx

    def undo_annotation(self):
        """
        Undo the previous annotation and update the display.
        """
        if self.prev_sort_alg is not None:

            self.sort_alg = self.prev_sort_alg
            self.save_obj['sort_alg'] = self.prev_sort_alg
            self.prev_sort_alg = None

            self.undo_label.place_forget()

            self.undo_csv_file()
            saves_handler.save_algorithm_pickle(self.save_obj)
            self.display_new_comparison()

            self.comp_count -= 1
            self.comp_count_label.configure(
                text='Comparison count: ' + str(self.comp_count) +
                '/' + str(self.sort_alg.get_comparison_max()))
            self.update_comparison_bar()

    def update_comparison_bar(self):
        """
        Update the comparison bar value based on the current comparison count.
        """
        self.comparison_bar.set(
            self.comp_count / self.sort_alg.get_comparison_max())

    def is_finished_check(self) -> bool:
        """
        Check if the sorting algorithm is finished.

        Returns:
            bool: True if the sorting algorithm is finished, False otherwise.
        """
        if self.sort_alg.is_finished():
            IsFinishedPopOut(self.root, self.back_to_menu)
            return True
        return False

    def save_sorted_images(self):
        """
        Save the sorted images to the appropriate directory.
        """
        res = self.sort_alg.get_result()
        for i, src in enumerate(res):
            _, extension = os.path.splitext(src)
            new_name = str(i) + extension
            dst = self.image_directory + '/sorted/' + new_name
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.relpath(self.image_directory + "/" + src), dst)

    def submit_comparison(
            self, keys: Union[str, List[str]],
            lvl: int, df_annotatation: bool = False):
        """
        Submit a comparison of images with their associated level.

        Args:
            keys (Union[str, List[str]]): The key or keys representing the 
                                          images being compared.
            lvl (int): The level associated with the comparison.
            df_annotatation (bool, optional): Whether it is a dataframe 
                                              annotation. Defaults to False.
        """
        if self.submission_timeout:
            return

        self.submission_timeout = True

        self.is_loading = True

        self.prev_sort_alg = copy.deepcopy(self.sort_alg)

        user = 'DF' if df_annotatation else self.user

        if type(self.sort_alg) == sa.TrueSkill:
            prev_ratings = copy.deepcopy(self.sort_alg.ratings)
            self.save_to_csv_file(keys, lvl, df_annotatation)
            self.sort_alg.inference(user, keys, lvl)
            conv.rmses_inference(self.save_obj, prev_ratings, self.sort_alg)

        else:
            self.sort_alg.inference(user, keys, lvl)
            self.save_to_csv_file(keys, lvl, df_annotatation)

        self.comp_count += 1
        self.comp_count_label.configure(
            text='Comparison count: ' + str(self.comp_count) +
            '/' + str(self.sort_alg.get_comparison_max()))

        if not type(self.sort_alg) == sa.RatingAlgorithm:
            self.comp_count_label.configure(
                text='Comparison count: ' + str(self.comp_count) +
                '/' + str(self.sort_alg.get_comparison_max()))
        else:
            self.comp_count_label.configure(
                text='Rating count: ' + str(self.comp_count) +
                '/' + str(self.sort_alg.get_comparison_max()))

        self.update_comparison_bar()

        saves_handler.save_algorithm_pickle(self.save_obj)

        self.session_elapsed_time_prev = time.time() - self.session_start_time

        if not self.is_finished_check():
            if (type(self.sort_alg) == sa.HybridTrueSkill and
                not self.sort_alg.is_rating and
                    not self.hybrid_transition_made):

                self.root.after_cancel(self.timer_after)
                # Switching modes popout
                self.reload_ordering_screen(self.save_obj)
                SwitchingModesPopOut(self.root)

            else:
                self.display_new_comparison()

        self.is_loading = False

        self.root.after(200, self.remove_submission_timeout)

    def remove_submission_timeout(self):
        """
        Remove the submission timeout flag.
        """
        self.submission_timeout = False

    def save_to_csv_file(
            self, res: Union[str, List[str]],
            lvls: Union[str, List[str]],
            df_annotatation: bool = False):
        """
        Save the result and level of the comparison to a CSV file.

        Args:
            res (Union[str, List[str]]): The result of the comparison.
            lvls (Union[str, List[str]]): The level associated with the 
                                          comparison.
            df_annotatation (bool, optional): Whether it is a dataframe 
                                              annotation. Defaults to False.
        """

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

        output_path = saves_handler.get_path_to_save(self.save_obj) + ".csv"
        df.to_csv(output_path, mode='a',
                  header=not os.path.exists(output_path), index=False)

    def undo_csv_file(self):
        """
        Undo the last entry in the CSV file by marking it as undone.
        """
        path = saves_handler.get_path_to_save(self.save_obj) + '.csv'
        copy_df = pd.read_csv(path)
        copy_df.iloc[-1, copy_df.columns.get_loc('undone')] = True
        copy_df.to_csv(path, index=False)

    def back_to_menu(self, remove_after: bool = True):
        """
        Return to the main menu.

        Args:
            remove_after (bool, optional): Whether to remove the timer. 
                                           Defaults to True.
        """
        if remove_after:
            self.root.after_cancel(self.timer_after)
        self.menu_callback()

    def submit_path(self, path: str):
        """
        Submit the image directory path and update the display.

        Args:
            path (str): The path to the image directory.
        """
        self.image_directory = path
        self.image_directory_located = True
        directory_dict = self.save_obj['user_directory_dict']
        directory_dict[self.user] = path
        saves_handler.save_algorithm_pickle(self.save_obj)
        self.display()
