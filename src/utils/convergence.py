import math
from typing import List

import numpy as np

import sorting_algorithms as sa
import utils.recomputation as recomp
import utils.saves_handler as saves_handler


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


def get_convergence(save: dict) -> List[float]:
    """
    Retrieves the convergence data from the given 'save' dictionary and provides 
    suitable representation of the RMS errors.

    Args:
        save (dict): The dictionary containing the necessary information.

    Returns:
        List[float]: A list containing the convergence data (RMS errors).
    """
    rmses = update_convergence_save(save)
    window = 10
    if (len(rmses) // (2*window)) > 0:
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


def moving_average(values: List[float], window: int) -> List[float]:
    """
    Computes the moving average of a given data list with a specified window size.

    Args:
        data (List[float]): A list of numerical values.
        window (int): The size of the window for moving average computation.

    Returns:
        List[float]: A list containing the moving average of the input data.
    """
    weights = np.repeat(1.0, window) / window
    return np.convolve(values, weights, 'valid')
