import numpy as np
import copy
import random

from abc import ABC, abstractmethod

class SortingAlgorithm (ABC):

    @abstractmethod
    def get_comparison(self):
        pass
    
    @abstractmethod
    def inference(self):
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

class MergeSort(SortingAlgorithm):

    def __init__(self,data):
        self.data = data
        self.current_layer = [[value] for value in data] 
        self.next_sorted = [[]] 

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
                layer = [smallest] + [equally_smallest] + self.current_layer.pop(0) + self.current_layer.pop(0)
            else:
                layer = [smallest] + self.current_layer.pop(0) + self.current_layer.pop(0)
            self.next_sorted[-1] += layer

            if len(self.current_layer) > 1:
                self.next_sorted.append([])  
            else:
                if  len(self.current_layer) == 1: 
                    self.next_sorted += [self.current_layer.pop(0)]  # add the remaining sublist to the next sorted layer
                self.current_layer = self.next_sorted  # update the current layer to the next sorted layer
                self.next_sorted = [[]]  # reset the next sorted layer

        else:
            # if neither of the two sublists in the current layer are empty, add the smallest element to the current nested list of the next sorted layer
            self.next_sorted[-1].append(smallest)
            if diff_lvls[0].value == 0:
                self.next_sorted[-1].append(equally_smallest)


    def get_result(self):
        if self.is_finished():
            # return the first and only sublist of the current layer if the sorting is finished
            return self.current_layer[0]

    def is_finished(self):
        # check if the first sublist in the current layer has the same number of elements as the original data
        return len(self.current_layer[0]) == len(self.data)

    def comparison_is_available(self, user_id):
        return not self.is_finished()

class TimSort(SortingAlgorithm):

    def __init__(self,data, min_runsize=32):
        self.data = list(data)
        self.current_layer = list(data)

        self.next_sorted = [[self.current_layer.pop(0)]] 
        self.min_runsize = min_runsize
        
        self.current_index = -1

        self.descending = False

        self.creating_runs = True

        self.high = -1
        self.low = -1

    def get_comparison(self, user_id):          
        if self.creating_runs:
            
            if self.current_index < 0:
                #Means that we are inserting a new value!
                self.current_index = len(self.next_sorted[-1]) - 1    
            return [self.current_layer[0], self.next_sorted[-1][self.current_index]]     
        else:
            return [self.current_layer[0][0], self.current_layer[1][0]]


    def inference(self, user_id, keys, diff_lvls):
        
        if self.creating_runs:
            self.bin_insertion_inference(user_id,keys,diff_lvls)
        else:
            self.merge_inference(user_id,keys,diff_lvls)
    
    def merge_inference(self, user_id, keys, diff_lvls):
        if self.current_layer[0][0] == keys[0]:
            smallest_i = 0
        else:            
            smallest_i = 1
        
        smallest = self.current_layer[smallest_i].pop(0)

        if diff_lvls[0].value == 0:
            equally_smallest = self.current_layer[1 - smallest_i].pop(0)
            

        if not self.current_layer[0] or not self.current_layer[1]:
            if diff_lvls[0].value == 0:
                layer = [smallest] + [equally_smallest] + self.current_layer.pop(0) + self.current_layer.pop(0)
            else:
                layer = [smallest] + self.current_layer.pop(0) + self.current_layer.pop(0)
            self.next_sorted[-1] += layer

            if len(self.current_layer) > 1:
                self.next_sorted.append([])  
            else:
                if  len(self.current_layer) == 1: 
                    self.next_sorted += [self.current_layer.pop(0)]  # add the remaining sublist to the next sorted layer
                self.current_layer = self.next_sorted  # update the current layer to the next sorted layer
                self.next_sorted = [[]]  # reset the next sorted layer

        else:
            # if neither of the two sublists in the current layer are empty, add the smallest element to the current nested list of the next sorted layer
            self.next_sorted[-1].append(smallest)
            if diff_lvls[0].value == 0:
                self.next_sorted[-1].append(equally_smallest)

    def bin_insertion_inference(self, user_id, keys, diff_lvls):
        # NOTE TO SELF! Does not use diff_lvls
        #If item we are inserting was smaller
        if keys[0] == self.current_layer[0]:
            #Check if this is start of a descending run
            if len(self.next_sorted[-1]) == 1:
                self.descending = True

            #Insert the item at the end of the list
            if self.descending:
                self.next_sorted[-1].append(self.current_layer.pop(0))
                self.current_index = -1
            else:
            #If it was ascending run, then it is not in its correct place
                if len(self.next_sorted[-1]) >= self.min_runsize:
                    #Run over!
                    self.next_sorted.append([self.current_layer.pop(0)])
                    self.current_index = -1
                elif self.current_index == 0:
                    self.next_sorted[-1].insert(self.current_index, self.current_layer.pop(0))
                    self.current_index -= 1
                else:
                    #Look at the next item (change this to binary search later?)
                    self.high = self.current_index
                    self.current_index = (self.low + self.high) // 2
        #If item we are inserting was bigger
        else:
            #Then not in its correct place!
            if self.descending:

                self.next_sorted[-1].reverse()
                self.descending = False

                if len(self.next_sorted[-1]) < self.min_runsize:
                    #Descending run was not found, reverse and start inserting into 
                    #ascending run like a normal person
                    self.current_index = len(self.next_sorted[-1]) - 1
                else:
                    #Run over!
                    self.next_sorted.append([self.current_layer.pop(0)])
                    self.current_index = -1
            else:
                if self.current_index == len(self.next_sorted[-1]) - 1:
                    self.next_sorted[-1].append(self.current_layer.pop(0))
                    self.current_index = -1
                    self.low = -1
                    self.high = -1
                else:
                    self.low = self.current_index
                    self.current_index = (self.low + self.high) // 2
                
                
        if self.high - self.low == 1:
            self.next_sorted[-1].insert(self.current_index+1, self.current_layer.pop(0)) 
            self.low = -1
            self.high = -1
            self.current_index = -1

        if len(self.current_layer) == 0:
            self.creating_runs = False
            self.current_layer = self.next_sorted
            self.next_sorted = [[]]

    def get_result(self):
        if self.is_finished():
            # return the first and only sublist of the current layer if the sorting is finished
            return self.current_layer[0]

    def is_finished(self):
        # check if the first sublist in the current layer has the same number of elements as the original data
        return not self.creating_runs and len(self.current_layer[0]) == len(self.data)        

    def comparison_is_available(self, user_id):
        return not self.is_finished()


class HammingLUCB(SortingAlgorithm):

    def __init__(self, data, delta, k, h, comparison_size=2):
        self.data = data
        self.delta = delta
        self.L = len(k) + 1
        self.k = sorted(k)
        self.h = h
        self.n = len(data)
        self.comparison_size = comparison_size
        self.data_dict = dict( zip( data,  np.zeros( (self.n,2) ) ) )
        self.comparisons = self.get_lists_to_compare()
        self.overlaps = [True] * (self.L-1)

    def get_lists_to_compare(self):
        data_shuff = random.sample(self.data, self.n)    
        (q, r) = divmod(self.n, self.comparison_size)
        comp_list = []
        for i in range(0,self.n,self.comparison_size):
            if r > 0 and i == q*self.comparison_size:
                comp_list.append(data_shuff[i:] + random.sample(data_shuff[:-r],self.comparison_size-r))
            else:
                comp_list.append(data_shuff[i:i+self.comparison_size])
        return comp_list

    def alpha_func(self, ind):
        u = self.data_dict[ind][1]
        delta_prime = self.delta / self.n
        
        # oldie from paper
        beta_func = np.log(1 / delta_prime) + 0.75 * np.log( np.log(1 / delta_prime)) + 1.5 * np.log(1+np.log(u/2))
        alpha = np.sqrt(beta_func/(2*u))      

        return alpha

    def get_comparison(self, user_id):
        if len(self.comparisons):
            return self.comparisons[0]
     
    def inference(self, user_id, keys, diff_lvls):

        self.comparisons.pop(0)
        self.update_estimates(keys, diff_lvls)

        if not len(self.comparisons):
            self.comparisons = self.get_new_comparisons()      


    def update_estimates(self, keys, diff_lvls):

        for i in range(len(keys)):
            j = i + 1 
            while j < len(keys):
                update = max([diff_lvl.value for diff_lvl in diff_lvls][i:j])

                self.data_dict[keys[i]][1] += 1
                self.data_dict[keys[j]][1] += 1
                
                T_i = self.data_dict[keys[i]][1]
                tau_i = self.data_dict[keys[i]][0]
                T_j = self.data_dict[keys[j]][1]
                tau_j = self.data_dict[keys[j]][0]

                if update > 0:
                    
                    self.data_dict[keys[i]][0] = ((T_i - 1)/T_i) * tau_i
                    self.data_dict[keys[j]][0] = ((T_j - 1)/T_j) * tau_j + 1/T_j

                    if update == 2:
                        self.data_dict[keys[i]][1] += 1
                        self.data_dict[keys[j]][1] += 1
                        
                        T_i = self.data_dict[keys[i]][1]
                        tau_i = self.data_dict[keys[i]][0]
                        T_j = self.data_dict[keys[j]][1]
                        tau_j = self.data_dict[keys[j]][0]


                        self.data_dict[keys[i]][0] = ((T_i - 1)/T_i) * tau_i
                        self.data_dict[keys[j]][0] = ((T_j - 1)/T_j) * tau_j + 1/T_j
 
                j += 1



    def get_new_comparisons(self):
        #Update overlaps
        self.update_overlaps()
        to_be_compared = []

        for i in range(len(self.overlaps)):            
            if self.overlaps[i]:
                S_tilde, _, S_lower = self.get_subsets(i)
                d_low, _ = self.get_d_lower(S_tilde)
                S_lower.append(d_low)
                intervals = {item: self.alpha_func(item) for item in S_lower}
                to_be_compared.append(max(intervals, key=intervals.get))

                S_tilde_next, S_upper_next, _ = self.get_subsets(i + 1)
                d_up, _ = self.get_d_upper(S_tilde_next)
                S_upper_next.append(d_up)
                intervals = {item: self.alpha_func(item) for item in S_upper_next}
                to_be_compared.append(max(intervals, key=intervals.get))
        
        keys = list(self.data_dict.keys())
        keys = [key for key in keys if key not in to_be_compared]

        comparisons = []

        for index in to_be_compared:
            randomed_ids = random.sample(keys, self.comparison_size - 1)
            randomed_ids.append(index)
            random.shuffle(randomed_ids)
            comparisons.append(randomed_ids)

        return comparisons

    def update_overlaps(self):
        for i in range(len(self.overlaps)):
            if(self.overlaps[i]):
                S_tilde_upper = (self.get_subsets(i)[0])
                S_tilde_lower = (self.get_subsets(i+1)[0])
                d1, d1_low = self.get_d_lower(S_tilde_upper)
                d2, d2_up = self.get_d_upper(S_tilde_lower)
                self.overlaps[i] = d1_low <= d2_up

    def get_d_upper(self, items):

        upper_bounds = {item: self.data_dict[item][0] + self.alpha_func(item) for item in items}
        index = max(upper_bounds, key=upper_bounds.get)
        return index, upper_bounds[index]

    def get_d_lower(self, items):

        lower_bounds = {item: self.data_dict[item][0] - self.alpha_func(item) for item in items}
        index = min(lower_bounds, key=lower_bounds.get)
        return index, lower_bounds[index]

    def get_subsets(self, l):
        if l == 0:
            start_index = 0
        else:
            start_index = self.k[l-1] + 1 + self.h

        if l == self.L - 1:
            stop_index = self.n - 1
        else:
            stop_index = self.k[l] - self.h
    
        sorted_ids = self.get_sorted()
        S_tilde = sorted_ids[start_index : stop_index + 1]
        S_upper = sorted_ids[start_index - self.h : start_index]
        S_lower = sorted_ids[stop_index + 1 : stop_index + 1 + self.h]

        return S_tilde, S_upper, S_lower

    def get_sorted(self):
        return [k for k, v in sorted(self.data_dict.items(), key=lambda item: item[1][0], reverse = True)]

    def get_result(self):
        return [k for k, v in sorted(self.data_dict.items(), key=lambda item: item[1][0])]

    def is_finished(self):
        return not any(self.overlaps)

    def comparison_is_available(self, user_id):
        return not self.is_finished()

class Borda(SortingAlgorithm):

    def __init__(self, data, comparison_size=2, counter_max = 20, exhaustive = False):
        self.data = list(data)
        self.n = len(data)
        self.borda_count = np.zeros(self.n)
        self.counter_iterations = 0 
        self.comparison_size = comparison_size    

        if exhaustive:
            self.counter_max = 1
            self.comparisons = self.exhaustive_to_compare()
        else: 
            self.counter_max = counter_max
            self.comparisons = self.get_lists_to_compare()

    def exhaustive_to_compare(self):
        to_compare = []
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    to_compare.append([i,j])
        random.shuffle(to_compare)
        return to_compare

    def get_lists_to_compare(self):
        data_shuff = random.sample(self.data, self.n)    
        (q, r) = divmod(self.n, self.comparison_size)
        comp_list = []
        for i in range(0,self.n,self.comparison_size):
            if r > 0 and i == q*self.comparison_size:
                comp_list.append(data_shuff[i:] + random.sample(data_shuff[:-r],self.comparison_size-r))
            else:
                comp_list.append(data_shuff[i:i+self.comparison_size])
        return comp_list
    
    def get_comparison(self, user_id):
        if len(self.comparisons):
            return self.comparisons[0]
     
    def inference(self, user_id, keys, diff_lvls):
        self.comparisons.pop(0)

        for i, id_ in enumerate(keys):
            index = self.data.index(id_)

            self.borda_count[index] += self.get_update_score(i, diff_lvls)

        if not self.comparisons and self.counter_iterations+1 < self.counter_max:
            self.counter_iterations += 1
            self.comparisons = self.get_lists_to_compare()

    def get_update_score(self, index, diff_lvls):
        
        accumulated_score = 0

        current_level = 0
        
        #count wins
        for i in reversed(range(index)):
            if diff_lvls[i].value > current_level:
                current_level = diff_lvls[i].value
            accumulated_score += current_level

        current_level = 0
        #count losses
        for i in range(index, len(diff_lvls)):
            if diff_lvls[i].value > current_level:
                current_level = diff_lvls[i].value
            accumulated_score -= current_level

        return accumulated_score
        


    def get_result(self):
        return [data_index for _, data_index in sorted(zip(self.borda_count,self.data))]

    def is_finished(self):
        return not self.comparisons and self.counter_iterations +1 == self.counter_max

    def comparison_is_available(self, user_id):
        return not self.is_finished()


class MergeTask:
    
    def __init__(self, lists, min_users = 3):

        self.lists = lists

        self.min_users = min_users

        self.user_orderings = {}

    def is_incomplete(self):
        return len(self.lists) < 2

    def register_user(self, user_id):
        
        assert user_id not in self.user_orderings

        self.user_orderings[user_id] = [copy.deepcopy(self.lists), []]

    def get_next_comparison(self, user_id):

        assert user_id in self.user_orderings
        
        return [self.user_orderings[user_id][0][0][0], self.user_orderings[user_id][0][1][0]]

    def user_is_registered(self, user_id):
        return user_id in self.user_orderings.keys()

    def active_users(self):
        return len(self.user_orderings)

    def user_inference(self, user_id, keys, diff_lvls):

        assert user_id in self.user_orderings

        list0 = self.user_orderings[user_id][0][0]
        list1 = self.user_orderings[user_id][0][1]

        if keys[0] == list0[0] or diff_lvls[0].value == 0:
            self.user_orderings[user_id][1].append(list0.pop(0))
        
        if keys[0] == list1[0] or diff_lvls[0].value == 0:
            self.user_orderings[user_id][1].append(list1.pop(0))

        #If either list 0 or 1 is empty 
        if not list0 or not list1:
            self.user_orderings[user_id][1] = self.user_orderings[user_id][1] + list0 + list1
            self.user_orderings[user_id][0] = []


                
    def user_is_finished(self, user_id):

        assert user_id in self.user_orderings

        return len(self.user_orderings[user_id][0]) == 0

    def is_finished(self):
        return sum([self.user_is_finished(user_id) for user_id in self.user_orderings.keys()]) >= self.min_users

class MultiCompTask:
    
    def __init__(self, items, min_users = 3):

        self.items = items

        self.min_users = min_users

        self.user_orderings = {}

    def is_incomplete(self):
        return len(self.items) < 2

    def register_user(self, user_id):
        
        assert user_id not in self.user_orderings

        self.user_orderings[user_id] = [copy.deepcopy(self.items), []]

    def get_next_comparison(self, user_id):

        assert user_id in self.user_orderings
        
        return self.items

    def user_is_registered(self, user_id):
        return user_id in self.user_orderings.keys()

    def active_users(self):
        return len(self.user_orderings)

    def user_inference(self, user_id, keys, diff_lvls):

        assert user_id in self.user_orderings
        assert set(self.items) == set(keys)

        self.user_orderings[user_id][1] = keys
                
    def user_is_finished(self, user_id):

        assert user_id in self.user_orderings

        return set(self.items) == set(self.user_orderings[user_id][1])

    def is_finished(self):
        return sum([self.user_is_finished(user_id) for user_id in self.user_orderings.keys()]) >= self.min_users
        

class MedianMergeSort(SortingAlgorithm):
    
    def __init__(self, data, comparison_size = 2):
        self.data = list(data)
        self.comparison_size = comparison_size
        self.items = [[item] for item in data]
        self.task_layers = [[]]
        self.get_lists_to_compare()
        #print([[t for t in l] for l in self.task_layers])

    def get_lists_to_compare(self):
        n = len(self.items)
        (q, r) = divmod(n, self.comparison_size)
        for i in range(0, n, self.comparison_size):
            if self.comparison_size <= 2:
                if r > 0 and i == q*self.comparison_size:
                    self.task_layers.append([MergeTask([self.items[-1]])])
    
                else:
                    self.task_layers[0].append(MergeTask(self.items[i:i+self.comparison_size]))
                    
            else:
                if  i == q*self.comparison_size:
                    if r > 1:
                        self.task_layers[0].append([MultiCompTask([self.data[-r:]])])
                    elif r == 1:
                        self.task_layers.append([MergeTask([self.items[-1]])])
                
                else:
                    self.task_layers[0].append(MultiCompTask(self.data[i:i+self.comparison_size]))
                    
            

    def get_comparison(self, user_id):

        ignore_user_amount = False

        while True:
            for layer in self.task_layers:
                for task in layer:
                    if task.user_is_registered(user_id) and not task.user_is_finished(user_id):
                        return task.get_next_comparison(user_id)
                    elif not task.user_is_registered(user_id) and not task.is_incomplete() and (task.active_users() < task.min_users or ignore_user_amount):
                        task.register_user(user_id)
                        return task.get_next_comparison(user_id)

            if ignore_user_amount:
                break

            ignore_user_amount = True

        raise Exception("Sorry, you have already completed all available " 
                    + "comparisons and must wait for other users to complete theirs")


    def inference(self, user_id, keys, diff_lvls):
        
        selected_task = None
        layer_idx = 0

        for i, layer in enumerate(self.task_layers):
            for task in layer:
                if task.user_is_registered(user_id) and not task.user_is_finished(user_id):
                    selected_task = task
                    layer_idx = i
                    break
        
        if not selected_task:
            raise Exception("You are not registered to any task :(")

        selected_task.user_inference(user_id,keys, diff_lvls)
        
        if selected_task.is_finished():
            averaged_list = self.get_mean_list(selected_task)

            if layer_idx + 1 == len(self.task_layers):
                self.task_layers.append([])

            #Add results to a Task in the next layer
            if self.task_layers[layer_idx + 1] and self.task_layers[layer_idx + 1][-1].is_incomplete():
                self.task_layers[layer_idx + 1][-1].lists.append(averaged_list)
            else:
                if len(self.task_layers[layer_idx]) == 1 and len(self.task_layers[layer_idx + 1]) != 0 :
                    if layer_idx + 2 == len(self.task_layers):

                        self.task_layers.append([])
                    
                    self.task_layers[layer_idx + 2].append(MergeTask([averaged_list]))

                else:
                    self.task_layers[layer_idx + 1].append(MergeTask([averaged_list]))

            self.task_layers[layer_idx].remove(selected_task)

        if not any(self.task_layers[0:layer_idx + 1]):
            self.task_layers = self.task_layers[layer_idx + 1:]

    def get_mean_list(self, task):

        means = []
        medians = []

        lists = [task.user_orderings[k][1] for k in task.user_orderings if task.user_is_finished(k)]

        for i in lists[0]:
            indices = [ordering.index(i) for ordering in lists]
            means.append(np.median(indices))

        data_means = dict(zip(lists[0],means))
        sorted_keys = [k for k, v in sorted(data_means.items(), key=lambda x:x[1])]
        
        return sorted_keys

    def comparison_is_available(self, user_id):
        for layer in self.task_layers:
                for task in layer:
                    if (not task.user_is_registered(user_id) and not task.is_incomplete()) or (task.user_is_registered(user_id) and not task.user_is_finished(user_id)):
                        return True
        return False

    def get_result(self):
        return self.task_layers[0][0].lists[0]

    def is_finished(self):
        return len(self.task_layers) == 1 and len(self.task_layers[0]) == 1 and self.task_layers[0][0].is_incomplete() 
    


from trueskill import Rating, quality_1vs1, rate_1vs1

class TrueSkill (SortingAlgorithm):

    def __init__(self, data, comparison_size = 2, comparison_max = 1000):

        self.n = len(data)
        self.data = list(data)

        self.ratings = {k:Rating() for k in data}
        self.overlap_matrix = np.full((self.n, self.n), self.intervals_overlap(self.data[0], self.data[1]))
        np.fill_diagonal(self.overlap_matrix, 0)

        self.comparison_size = comparison_size
        self.comparison_max = comparison_max
        self.comparison_counter = 0
    
    def intervals_overlap(self, key1, key2):
        r1_low = self.ratings[key1].mu - 2 * self.ratings[key1].sigma
        r1_high = self.ratings[key1].mu + 2 * self.ratings[key1].sigma

        r2_low = self.ratings[key2].mu - 2 * self.ratings[key2].sigma
        r2_high = self.ratings[key2].mu + 2 * self.ratings[key2].sigma

        return (min(r1_high,r2_high) - max(r1_low,r2_low))/(max(r1_high,r2_high) - min(r1_low,r2_low)) * max(r1_high-r1_low,r2_high-r2_low)

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

        for i in range(self.n):
            indices = np.argpartition(self.overlap_matrix[i], -self.comparison_size+1)[-self.comparison_size+1:]
            indices = [ind for ind in indices if self.overlap_matrix[i][ind] > 0]

            sum_i = sum(self.overlap_matrix[i][indices])
            if max_sum < sum_i:
                max_sum = sum_i
                comparisons = [i] + list(indices)
        return comparisons


    def inference(self, user_id, keys, diff_lvls):

        to_update = []

        for i in range(len(keys)):
            j = i + 1 
            while j < len(keys):
                update = max([diff_lvl.value for diff_lvl in diff_lvls][i:j])
                
                if update == 0:
                    to_update.append(([i,j],True))

                else:
                    to_update.append(([i,j],False))
                    if update == 2:
                        to_update.append(([i,j],False))
                j += 1
                
        random.shuffle(to_update)
        
        for ([i,j], is_draw) in to_update:
            if is_draw:
                self.ratings[keys[j]], self.ratings[keys[i]] = rate_1vs1(self.ratings[keys[j]],self.ratings[keys[i]], drawn=True)
            else:
                self.ratings[keys[j]], self.ratings[keys[i]] = rate_1vs1(self.ratings[keys[j]],self.ratings[keys[i]])
        
        for k in keys:
            self.update_overlap_matrix(k)

        self.comparison_counter += 1

    def get_result(self):
        return [k for k, v in sorted(self.ratings.items(), key=lambda x:x[1])]

    def is_finished(self):
        return self.comparison_counter == self.comparison_max or self.overlap_matrix.max() <= 0

    def comparison_is_available(self, user_id):
        return not self.is_finished()