import os
import pickle
import random
import sys
import time
from pathlib import Path
from typing import List, Optional

import pandas as pd

import sorting_algorithms as sa


def save_algorithm_pickle(save):
    """
    Save the current state of the algorithm to a pickle file.
    """
    f = open(get_full_path(
        save["path_to_save"] + ".pickle"), "wb")
    pickle.dump(save, f)
    f.close()


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

    path = get_full_path("/saves")

    if not os.path.exists(path):
        os.makedirs(path)

    path_to_save = path + "/" + file_name

    df = pd.DataFrame(
        columns=['result', 'diff_levels', 'time', 'session', 'user',
                 'undone', 'type'])

    df.to_csv(path_to_save + ".csv", index=False)

    rel_path_to_save = "/saves/" + file_name
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

    f = open(path_to_save + ".pickle", "wb")
    pickle.dump(save_obj, f)
    f.close()


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
        print(path)
        application_path = str(Path(os.path.dirname(__file__)).parent.parent)

        print(application_path)

    path = application_path + "/" + path
    print(path)
    return path.replace("\\", "/")
