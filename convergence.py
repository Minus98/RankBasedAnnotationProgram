import math
from typing import List

import numpy as np

import recomputation as recomp
import saves_handler
import sorting_algorithms as sa


def update_convergence_save(save: dict) -> List[float]:
    """
    Computes and returns the RMS errors for the provided 'save'.

    Args:
        save (dict): The dictionary containing the necessary information.

    Returns:
        List[float]: The computed RMS errors.
    """
    if type(save['sort_alg']) == sa.TrueSkill:
        if "rmses" not in save or not len(
                save["rmses"]) == (save["sort_alg"].comp_count-1):
            _, save["rmses"] = recomp.recompute_trueskill(save)
            saves_handler.save_algorithm_pickle(save)
    elif type(save['sort_alg']) == sa.HybridTrueSkill:
        if not save["sort_alg"].is_rating or "rmses" not in save or not len(
                save["rmses"]) == (save["sort_alg"].sort_alg.comp_count-1):
            _, save["rmses"] = recomp.recompute_hybridtrueskill(save)
            saves_handler.save_algorithm_pickle(save)
    else:
        if "rmses" not in save:
            save["rmses"] = []
            saves_handler.save_algorithm_pickle(save)

    return save["rmses"]


def get_convergence(save):
    rmses = update_convergence_save(save)
    window = 10
    if len(rmses) // 3 > 0:
        return moving_average(rmses, window)
    return rmses


def rmses_inference(save: dict, prev_ratings: dict, sort_alg: sa.TrueSkill):
    """
    Computes RMS errors for the provided 'save' using the appropriate algorithm and 
    saves the results.

    Args:
        save (dict): The dictionary containing the necessary information.
        prev_ratings (dict): The previous ratings dictionary.
        sort_alg (TrueSkill): The TrueSkill sorting algorithm.
    """
    update_convergence_save(save)
    rmse = math.sqrt(
        sum(
            (prev_ratings[key].mu - sort_alg.ratings[key].mu) ** 2
            for key in sort_alg.data) / sort_alg.n)
    save["rmses"].append(rmse)
    saves_handler.save_algorithm_pickle(save)


def moving_average(values, window):
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')
