import copy
import math

import pandas as pd

import saves_handler
import sorting_algorithms
import utils


def get_convergence(save):

    print(save)

    if "rmses" in save and len(
            save["rmses"]) == (save["sort_alg"].comp_count-1):
        print('yep')
        pass

    else:
        save["rmses"] = recompute_algorithms(save)
        saves_handler.save_algorithm_pickle(save)

    return save["rmses"]


def recompute_algorithms(save):
    if type(save['sort_alg']) == sorting_algorithms.TrueSkill:
        return recompute_trueskill(save)
    elif type(save['sort_alg']) == sorting_algorithms.RatingAlgorithm:
        # TODO
        pass
    elif type(save['sort_alg']) == sorting_algorithms.HybridTrueSkill:
        # TODO
        pass
    elif type(save['sort_alg']) == sorting_algorithms.MergeSort:
        # TODO
        pass

    return None


def recompute_trueskill(save):
    csv = pd.read_csv(save['path_to_save'] + '.csv')
    sort_alg = sorting_algorithms.TrueSkill(
        data=save['sort_alg'].data,
        comparison_max=save['sort_alg'].comparison_max)
    rmses = []

    for i, i_df in csv.iterrows():
        res = i_df['result'].replace(
            "[", "").replace(
            "]", "").replace(
            "'", "").split(", ")

        diff_lvls = [
            sorting_algorithms.DiffLevel(
                abs([int(s) for s in dl if s.isdigit()][0]))
            for dl in i_df['diff_levels'].split(", ")]

        if i_df['undone'] == True:
            pass
        else:
            sort_alg.inference(i_df['user'], res, diff_lvls)

            if i > 0:
                rmse = math.sqrt(sum(
                    (prev_ratings[key].mu - sort_alg.ratings[key].mu)
                    ** 2 for key in sort_alg.data) / sort_alg.n)
                rmses.append(rmse)

            prev_ratings = copy.deepcopy(sort_alg.ratings)

    return rmses
