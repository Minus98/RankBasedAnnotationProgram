import copy
import random

import numpy as np

from abc import ABC, abstractmethod
from trueskill import Rating, rate_1vs1


class SortingAlgorithm (ABC):

    @abstractmethod
    def get_comparison(self, user_id: str) -> list[str]:
        '''Fetches a new comparison based on the state of the sorting algorithm.

        Args:
            user_id (str): the id of the user that is to perform the comparison.
        Returns:
            a list containing the keys of the elements that are to be compared.'''
        
        pass

    @abstractmethod
    def inference(self):
        '''Updates the algorithms estimated ordering based on the results of a comparison.
        '''
        pass

    @abstractmethod
    def get_result(self):
        pass

    @abstractmethod
    def is_finished(self):
        pass

    @abstractmethod
    def comparison_is_available(self, user_id):
        pass

    @abstractmethod
    def get_comparison_count(self):
        pass

    @abstractmethod
    def get_comparison_max(self):
        pass


class MergeSort(SortingAlgorithm):

    def __init__(self, data):
        self.data = data
        self.comparison_size = 2
        self.current_layer = [[value] for value in data]
        self.next_sorted = [[]]
        self.comp_count = 0

    def get_comparison(self, user_id):
        return [self.current_layer[0][0], self.current_layer[1][0]]

    def inference(self, user_id, keys, diff_lvls):
        if self.current_layer[0][0] == keys[0]:
            smallest_i = 0
        else:
            smallest_i = 1

        smallest = self.current_layer[smallest_i].pop(0)

        if diff_lvls[0].value == 0:
            equally_smallest = self.current_layer[1 - smallest_i].pop(0)

        if not self.current_layer[0] or not self.current_layer[1]:
            if diff_lvls[0].value == 0:
                layer = [smallest] + [equally_smallest] + \
                    self.current_layer.pop(0) + self.current_layer.pop(0)
            else:
                layer = [smallest] + \
                    self.current_layer.pop(0) + self.current_layer.pop(0)
            self.next_sorted[-1] += layer

            if len(self.current_layer) > 1:
                self.next_sorted.append([])
            else:
                if len(self.current_layer) == 1:
                    # add the remaining sublist to the next sorted layer
                    self.next_sorted += [self.current_layer.pop(0)]
                # update the current layer to the next sorted layer
                self.current_layer = self.next_sorted
                self.next_sorted = [[]]  # reset the next sorted layer

        else:
            # if neither of the two sublists in the current layer are empty, add the smallest element to the current nested list of the next sorted layer
            self.next_sorted[-1].append(smallest)
            if diff_lvls[0].value == 0:
                self.next_sorted[-1].append(equally_smallest)

        self.comp_count += 1

    def get_result(self):
        if self.is_finished():
            # return the first and only sublist of the current layer if the sorting is finished
            return self.current_layer[0]

    def is_finished(self):
        # check if the first sublist in the current layer has the same number of elements as the original data
        return len(self.current_layer[0]) == len(self.data)

    def comparison_is_available(self, user_id):
        return not self.is_finished()

    def get_comparison_count(self):
        return self.comp_count

    def get_comparison_max(self):
        # Fix me pleeeez
        return 0


class TrueSkill (SortingAlgorithm):

    def __init__(self, data, comparison_size=2, comparison_max=None, initial_mus=None, random_comparisons=False):

        self.n = len(data)
        self.data = list(data)
        self.random_comparisons = random_comparisons

        if comparison_max is None:
            self.comparison_max = self.n * 6
        else:
            self.comparison_max = comparison_max

        if initial_mus:
            self.ratings = {k: Rating(initial_mus[k]) for k in data}
        else:
            self.ratings = {k: Rating() for k in data}

        self.overlap_matrix = np.full(
            (self.n, self.n), self.intervals_overlap(self.data[0], self.data[1]))
        np.fill_diagonal(self.overlap_matrix, 0)

        self.comparison_size = comparison_size
        self.comp_count = 0

        self.user_comparisons = {}

    def intervals_overlap(self, key1, key2):
        r1_low = self.ratings[key1].mu - 2 * self.ratings[key1].sigma
        r1_high = self.ratings[key1].mu + 2 * self.ratings[key1].sigma

        r2_low = self.ratings[key2].mu - 2 * self.ratings[key2].sigma
        r2_high = self.ratings[key2].mu + 2 * self.ratings[key2].sigma

        return (min(r1_high, r2_high) - max(r1_low, r2_low))/(max(r1_high, r2_high) - min(r1_low, r2_low)) * max(r1_high-r1_low, r2_high-r2_low)

    def update_overlap_matrix(self, key):
        key_i = self.data.index(key)

        for i in range(self.n):
            if i != key_i:
                overlap = self.intervals_overlap(key, self.data[i])
                self.overlap_matrix[i][key_i] = overlap
                self.overlap_matrix[key_i][i] = overlap

    def get_comparison(self, user_id):
        max_sum = 0
        comparisons = []

        if user_id not in self.user_comparisons:
            self.user_comparisons[user_id] = np.ones(self.overlap_matrix.shape)

        if self.random_comparisons and self.comparison_size == 2:
            comparisons = random.sample(range(self.n), 2)
        else:

            masked_overlap_matrix = np.multiply(
                self.overlap_matrix, self.user_comparisons[user_id])

            for i in range(self.n):
                if self.comparison_size == 2:

                    max_index = np.argmax(masked_overlap_matrix[i])

                    if masked_overlap_matrix[i][max_index] > max_sum:

                        max_sum = masked_overlap_matrix[i][max_index]
                        comparisons = [i, max_index]

                else:
                    indices = np.argpartition(
                        self.overlap_matrix[i], -self.comparison_size+1)[-self.comparison_size+1:]
                    indices = [
                        ind for ind in indices if self.overlap_matrix[i][ind] > 0]

                    sum_i = sum(self.overlap_matrix[i][indices])
                    if max_sum < sum_i:
                        max_sum = sum_i
                        comparisons = [i] + list(indices)

        keys_output = [list(self.ratings.keys())[c] for c in comparisons]

        return keys_output

    def inference(self, user_id, keys, diff_lvls):

        to_update = []

        for i in range(len(keys)):
            j = i + 1
            while j < len(keys):
                update = max([diff_lvl.value for diff_lvl in diff_lvls][i:j])

                if update == 0:
                    to_update.append(([i, j], True))

                else:
                    to_update.append(([i, j], False))
                    if update == 2:
                        to_update.append(([i, j], False))
                j += 1

        random.Random(6).shuffle(to_update)

        for ([i, j], is_draw) in to_update:
            if is_draw:
                self.ratings[keys[j]], self.ratings[keys[i]] = rate_1vs1(
                    self.ratings[keys[j]], self.ratings[keys[i]], drawn=True)
            else:
                self.ratings[keys[j]], self.ratings[keys[i]] = rate_1vs1(
                    self.ratings[keys[j]], self.ratings[keys[i]])

        for k in keys:
            self.update_overlap_matrix(k)

        self.comp_count += 1

        if user_id not in self.user_comparisons:
            self.user_comparisons[user_id] = np.ones(self.overlap_matrix.shape)

        key_i = self.data.index(keys[i])
        key_j = self.data.index(keys[j])

        self.user_comparisons[user_id][key_i, key_j] = 0
        self.user_comparisons[user_id][key_j, key_i] = 0

    def get_result(self):
        return [k for k, _ in sorted(self.ratings.items(), key=lambda x:x[1])]

    def is_finished(self):

        if self.comp_count >= self.comparison_max or self.overlap_matrix.max() <= 0:
            return True

        return False

    def comparison_is_available(self, user_id):
        return not self.is_finished() or not self.get_comparison(user_id)

    def get_comparison_count(self):
        return self.comp_count

    def get_comparison_max(self):
        return self.comparison_max


class RatingAlgorithm (SortingAlgorithm):

    def __init__(self, data):

        self.n = len(data)
        self.data = list(data)

        self.comp_count = 0
        self.comparison_size = 1
        self.user_ratings = {}

    def get_comparison(self, user_id):
        user_dict = self.get_user(user_id)
        if user_dict['toRate']:
            return user_dict['toRate'][0]
        return []

    def get_user(self, user_id):
        if user_id not in self.user_ratings:
            user_hash = abs(hash(user_id)) % (10 ** 8)
            to_sort = copy.deepcopy(self.data)
            random.Random(user_hash).shuffle(to_sort)
            self.user_ratings[user_id] = {
                'toRate': to_sort, 'rated': {}}
        return self.user_ratings[user_id]

    def inference(self, user_id, key, rating):

        user_dict = self.get_user(user_id)

        if key in user_dict['toRate']:
            user_dict['toRate'].remove(key)
            user_dict['rated'][key] = rating
            self.comp_count += 1

    def get_result(self):
        return {user: self.get_user_result(user) for user in self.user_ratings.keys()}

    def get_user_result(self, user_id):
        user_dict = self.get_user(user_id)
        return user_dict['rated']

    def is_finished(self):
        return False  # never finished

    def comparison_is_available(self, user_id):
        user_dict = self.get_user(user_id)
        if len(user_dict['toRate']):
            return True
        return False

    def get_comparison_count(self):
        return self.comp_count

    def get_comparison_max(self):
        return len(self.data)


class HybridTrueSkill (SortingAlgorithm):

    def __init__(self, data, comparison_size=2, comparison_max=None):

        self.data = data
        self.comparison_size = comparison_size
        self.comparison_max = comparison_max

        self.sort_alg = RatingAlgorithm(data)
        self.is_rating = True

    def get_comparison(self, user_id):
        return self.sort_alg.get_comparison("hybrid")

    def inference(self, user_id, key, rating):
        self.sort_alg.inference("hybrid", key, rating)

        if self.is_rating:
            if not self.sort_alg.comparison_is_available("hybrid"):
                self.change_to_trueskill("hybrid")

    def get_result(self):
        return self.sort_alg.get_result()

    def is_finished(self):
        return self.sort_alg.is_finished()

    def comparison_is_available(self, user_id):
        return self.sort_alg.comparison_is_available("hybrid")

    def change_to_trueskill(self, user_id):
        results = {k: self.rating_to_mu(
            v) for k, v in self.sort_alg.get_user_result("hybrid").items() if v > 0}

        self.sort_alg = TrueSkill(results.keys(), comparison_size=self.comparison_size,
                                  comparison_max=len(results.keys())*4, initial_mus=results)
        self.is_rating = False

    def rating_to_mu(self, rating):
        # With mu = 25 and 1/2 standard deviation spacing
        return 25 + ((rating - 1) * 2 + 1) / 4 * 8.333

    def get_comparison_count(self):

        total = self.sort_alg.get_comparison_count()
        if not self.is_rating:
            total += len(self.data)

        return total

    def get_comparison_max(self):
        return self.sort_alg.get_comparison_max()
