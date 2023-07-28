import copy
import math
from typing import List

import pandas as pd

import saves_handler
import sorting_algorithms as sa


def get_convergence(save: dict) -> List[float]:
    """
    Computes and returns the RMS errors for the provided 'save'.

    Args:
        save (dict): The dictionary containing the necessary information.

    Returns:
        List[float]: The computed RMS errors.
    """

    if "rmses" not in save or not len(
            save["rmses"]) == (save["sort_alg"].comp_count-1):
        create_rmses_from_recomputation(save)

    return save["rmses"]


def create_rmses_from_recomputation(save: dict) -> None:
    """
    Computes RMS errors for the provided 'save' using the appropriate algorithm.

    Args:
        save (dict): The dictionary containing the necessary information.
    """
    if type(save['sort_alg']) == sa.TrueSkill:
        save["rmses"] = recompute_trueskill(save)
        saves_handler.save_algorithm_pickle(save)


def rmses_inference(save: dict, prev_ratings: dict, sort_alg: sa.TrueSkill):
    """
    Computes RMS errors for the provided 'save' using the appropriate algorithm and saves the results.

    Args:
        save (dict): The dictionary containing the necessary information.
        prev_ratings (dict): The previous ratings dictionary.
        sort_alg (TrueSkill): The TrueSkill sorting algorithm.
    """
    if "rmses" not in save or not len(
            save["rmses"]) == (save["sort_alg"].comp_count-1):
        create_rmses_from_recomputation(save)
    save["rmses"].append(calc_rmse(prev_ratings, sort_alg))
    saves_handler.save_algorithm_pickle(save)
    print(save["rmses"])


def calc_rmse(prev_ratings: dict, sort_alg: sa.TrueSkill) -> float:
    """
    Calculates the Root Mean Square Error (RMSE) between previous ratings and current ratings.

    Args:
        prev_ratings (dict): The previous ratings dictionary.
        sort_alg (TrueSkill): The TrueSkill sorting algorithm.

    Returns:
        float: The computed RMSE.
    """
    rmse = math.sqrt(
        sum(
            (prev_ratings[key].mu - sort_alg.ratings[key].mu) ** 2
            for key in sort_alg.data) / sort_alg.n)
    return rmse


def recompute_trueskill(save: dict) -> List[float]:
    """
    Recomputes TrueSkill algorithm based on the data in 'save' and returns the RMS errors.

    Args:
        save (dict): The dictionary containing the necessary information.

    Returns:
        List[float]: The computed RMS errors.
    """
    csv = pd.read_csv(save['path_to_save'] + '.csv')
    sort_alg = sa.TrueSkill(
        data=save['sort_alg'].data,
        comparison_max=save['sort_alg'].comparison_max)
    rmses = []

    for i, i_df in csv.iterrows():
        res = i_df['result'].replace(
            "[", "").replace(
            "]", "").replace(
            "'", "").split(", ")

        diff_lvls = [
            sa.DiffLevel(
                abs([int(s) for s in dl if s.isdigit()][0]))
            for dl in i_df['diff_levels'].split(", ")]

        if i_df['undone'] == True:
            pass
        else:
            sort_alg.inference(i_df['user'], res, diff_lvls)

            if i > 0:
                rmses.append(calc_rmse(prev_ratings, sort_alg))

            prev_ratings = copy.deepcopy(sort_alg.ratings)

    return rmses
