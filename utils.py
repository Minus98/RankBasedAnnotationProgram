import os
import pickle
import random
import sys
import time
from enum import Enum
from pathlib import Path
from typing import List, Optional

import customtkinter as ctk
import pandas as pd

import sorting_algorithms as sa


class DiffLevel(Enum):
    none = 0
    normal = 1
    major = 2


def remove_hover(widget: ctk.CTkBaseClass):

    widget.unbind("<Enter>")
    widget.unbind("<Leave>")

    for child in widget.winfo_children():
        remove_hover(child)


def add_hover(widget: ctk.CTkBaseClass):
    """
    Add hover effect to the widget and its children.

    Args:
        widget (CTkBaseClass): The widget to add the hover effect to.
    """

    add_hover_to_children(widget, widget)


def add_hover_to_children(widget: ctk.CTkBaseClass,
                          child_widget: ctk.CTkBaseClass):
    """
    Add hover effect to the child ctk widget and its children.

    Args:
        widget: The parent ctk widget.
        child_widget: The child ctk widget to add the hover effect to.
    """

    child_widget.bind("<Enter>", lambda event, widget=widget,
                      color=widget.cget("fg_color"): highlight(widget, color))
    child_widget.bind(
        "<Leave>", lambda event, widget=widget,
        color=widget.cget("fg_color"): remove_highlight(widget, color))

    for child in child_widget.winfo_children():
        add_hover_to_children(widget, child)


def highlight(widget: ctk.CTkBaseClass, og_color: List[str]):
    """
    Add highlight effect to the ctk widget by changing its foreground color.

    Args:
        widget: The ctk widget to highlight.
        color: The original foreground color of the widget.
    """
    gray_color = int(og_color[1][-2:]) + 10

    if gray_color > 100:
        gray_color = 100

    widget.configure(fg_color='gray' + str((gray_color)))


def remove_highlight(widget: ctk.CTkBaseClass, og_color: List[str]):
    """
    Remove highlight effect from the ctk widget by restoring its original 
    foreground color.

    Args:
        widget: The ctk widget to remove the highlight effect from.
        color: The original foreground color of the widget.

    """
    widget.configure(fg_color=og_color)


def get_full_path(path: str) -> str:
    """
    Get the full path of a file or directory.

    Args:
        path: The relative path.

    Returns:
        str: The full path.
    """

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    path = application_path + "/" + path
    return path.replace("\\", "/")


def highlight_label(label: ctk.CTkLabel):
    """
    Highlight the label by adjusting its text color.

    Args:
        label (CTkLabel): The widget containing the label to be highlighted.
    """

    hex = label.cget("text_color")

    rgb = [int(hex[i:i+2], 16) for i in (1, 3, 5)]
    for i in range(len(rgb)):
        rgb[i] = min(rgb[i]+50, 255)

    new_hex = '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    label.configure(text_color=new_hex)


def remove_highlight_label(label: ctk.CTkLabel):
    """
    Remove the highlight from the label by setting its text color to a 
    default value.

    Args:
        label (CTkLabel): The label from which to remove the highlight.
    """

    label.configure(text_color="#777777")


def create_save(
        name: str, algorithm: str, comparison_size: int, image_directory: str,
        scroll_enabled: bool, rating_buttons: Optional[List[str]] = None,
        rating_prompt: Optional[str] = None,
        custom_rankings: Optional[List[str]] = None,
        ranking_prompt: Optional[str] = None, comp_max: Optional[int] = None):
    """
    Creates and saves the annotation item.

    Args:
        name (str): Name of the annotation item.
        algorithm (str): Selected algorithm for sorting the images.
        comparison_size (int): The size of the comparison.
        image_directory (str): Directory path containing the image files.
        scroll_enabled (bool): A boolean indicating whether scrolling is enabled.
        rating_buttons (Optional[List[str]]): A list containing the buttons which should
                                              be available when rating.
        rating_prompt (Optional[str]): A new prompt which users are given when rating.
        custom_rankings (Optional[List[str]]): A list containing the options available
                                               when ranking.
        ranking_prompt (Optional[str]): A new prompt which users are given when ranking.
        comp_max (Optional[int]): The total amount of allowed comparisons.
    """

    directory = os.path.relpath(image_directory)
    img_paths = list(str(os.path.basename(p))
                     for p in Path(directory).glob("**/*")
                     if p.suffix
                     in {'.jpg', '.png', '.nii'} and 'sorted'
                     not in str(p).lower())

    random.shuffle(img_paths)

    if algorithm == "Merge Sort":
        sort_alg = sa.MergeSort(data=img_paths)
    elif algorithm == "Rating":
        sort_alg = sa.RatingAlgorithm(data=img_paths)
    elif algorithm == "Hybrid":
        sort_alg = sa.HybridTrueSkill(
            data=img_paths, comparison_size=comparison_size,
            comparison_max=comp_max)
    else:
        sort_alg = sa.TrueSkill(
            data=img_paths, comparison_size=comparison_size,
            comparison_max=comp_max)

    file_name = str(int(time.time()))

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    path = application_path + "/saves"

    if not os.path.exists(path):
        os.makedirs(path)

    path_to_save = path + "/" + file_name

    df = pd.DataFrame(
        columns=['result', 'diff_levels', 'time', 'session', 'user',
                 'undone', 'type'])

    df.to_csv(path_to_save + ".csv", index=False)

    rel_path_to_save = "saves/" + file_name
    save_obj = {
        "sort_alg": sort_alg,
        "name": name,
        "image_directory": directory,
        "path_to_save": rel_path_to_save,
        "user_directory_dict": {},
        "scroll_allowed": scroll_enabled}

    if rating_buttons:
        save_obj["custom_ratings"] = rating_buttons

    if rating_prompt:
        save_obj["custom_rating_prompt"] = rating_prompt

    if custom_rankings:
        save_obj["custom_rankings"] = custom_rankings

    if ranking_prompt:
        save_obj["custom_ranking_prompt"] = ranking_prompt

    f = open(path + "/" + file_name + ".pickle", "wb")
    pickle.dump(save_obj, f)
    f.close()
