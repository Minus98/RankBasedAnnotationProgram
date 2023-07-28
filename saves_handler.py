import pickle

import utils


def save_algorithm_pickle(save):
    """
    Save the current state of the algorithm to a pickle file.
    """
    f = open(utils.get_full_path(
        save["path_to_save"] + ".pickle"), "wb")
    pickle.dump(save, f)
    f.close()
