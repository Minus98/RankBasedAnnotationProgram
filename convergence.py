import math
from typing import List

import recomputation as recomp
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


def rmses_inference(save: dict, prev_ratings: dict, sort_alg: sa.TrueSkill):
    """
    Computes RMS errors for the provided 'save' using the appropriate algorithm and 
    saves the results.

    Args:
        save (dict): The dictionary containing the necessary information.
        prev_ratings (dict): The previous ratings dictionary.
        sort_alg (TrueSkill): The TrueSkill sorting algorithm.
    """
    get_convergence(save)
    rmse = math.sqrt(
        sum(
            (prev_ratings[key].mu - sort_alg.ratings[key].mu) ** 2
            for key in sort_alg.data) / sort_alg.n)
    save["rmses"].append(rmse)
    saves_handler.save_algorithm_pickle(save)
