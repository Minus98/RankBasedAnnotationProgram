import matplotlib.pyplot as plt
from statistics import NormalDist
from enum import Enum
import pandas as pd
import numpy as np
import random

class Simulation:

    def __init__(self, data, comparison_clearness = 10, use_diff_levels = True, k = [0.2,0.4,0.6,0.8]):
        self.data = data
        self.k = k
        self.sorted_data = {k:v for k, v in sorted(data.items(), key=lambda x:x[1])}
        self.comparison_clearness = comparison_clearness
        
        self.users =   [User(data, 1, comparison_clearness, use_diff_levels),
                        User(data, 2, comparison_clearness, use_diff_levels),
                        User(data, 3, comparison_clearness, use_diff_levels),
                        User(data, 4, comparison_clearness, use_diff_levels)]

    def run(self, sort_alg, max_count=np.inf, use_df=True):
        df_init_data = [[[] for j in self.data.keys()] for i in self.data.keys()]
        df = pd.DataFrame(df_init_data, columns = self.data.keys(),index = self.data.keys())

        count = 0
        df_count = 0
        while not sort_alg.is_finished() and count < max_count:
            for user in self.users:
                while sort_alg.comparison_is_available(user.identifier) and not sort_alg.is_finished() and count < max_count:
                    
                    to_rank = sort_alg.get_comparison(user.identifier)
                    #print(to_rank)
                    df_info = get_df_annotation(df, to_rank[0],to_rank[1])

                    if df_info and use_df and len(to_rank) == 2:
                        df_count += 1
                        keys = df_info
                        diff_lvls = np.full(len(keys)-1, DiffLevel.normal)
                        
                    else:
                        count += 1
                        keys, diff_lvls = user.get_sorted(to_rank)
                        update_data(keys, df)
                    
                    sort_alg.inference(user.identifier, keys, diff_lvls)

        sorted_keys = sort_alg.get_result()
        sorted_vals = [self.data[k] for k in sorted_keys]

        acc = self.accuracy(sorted_keys) 

        if df_count > 0 :
            print("Number of comparisions: ", count, "           Number of comparisions from df: ", df_count) 
           
        else:
            print("Number of comparisions: ", count)
        print("Label accuracy: ", np.round(acc*100), "%\n")
        print("Sorted indexes:   ", sorted_keys)
        print("Sorted values:    ", sorted_vals)

        print("\nCorrect indexes:  ", list(self.sorted_data.keys()))
        print("Correct values:   ", list(self.sorted_data.values()))

        return sorted_keys, sorted_vals, count, acc, df

    def accuracy(self,y_pred):
        y_true = list(self.sorted_data)
        intersections = 0
        for i in range(len(self.k)+1):
            start = self.k[i-1] if i > 0 else 0
            end = self.k[i] if i < len(self.k) else 1

            start_idx = int(start*len(y_true))
            end_idx = int(end*len(y_true))

            y_t = set(y_true[start_idx:end_idx])
            y_p = set(y_pred[start_idx:end_idx])
            
            set_inter = len(y_t.intersection(y_p))
            intersections += set_inter

        return intersections / len(y_true)

def gen_data(size=100):
    identification = range(size)
    values = np.random.randint(low = 1, high = len(identification)*2, size = len(identification))
    return dict(zip(identification,values))

def get_df_annotation(df, val_1,val_2):
    keys = df[val_2][val_1] # val_1 < val_2
    if len(keys) >= 3:
        diff = sum(keys) / len(keys)
        if diff <= 0.3:
            return [val_1,val_2]
        elif diff >= 0.6:
            return [val_2,val_1]
    return []

def plot_sorting(data, labels, values):
    plt.figure(figsize=(10, 6))
    plt.plot(sorted(data.values()), label="True order")

    for i in range(len(labels)):
        plt.plot(values[i], label=labels[i])

    plt.legend(loc='upper right')
    plt.xlabel("rank")
    plt.ylabel("value")
    plt.show() 

def update_data(ranked_list, df):
    comparisions = [[a, b] for idx, a in enumerate(ranked_list) for b in ranked_list[idx + 1:]]
    for [a, b] in comparisions:
        df[a][b].append(1) # a is larger than b
        df[b][a].append(0) # a is smaller than b

class DiffLevel(Enum):
    none = 0
    normal = 1
    major = 2

class User():

    def __init__(self, data, identifier, comparison_clearness=10, use_diff_levels = True):
        self.identifier = identifier
        self.sigma = len(data)/100
        self.value_perception = {k:np.random.normal(data[k],self.sigma) for k in data}
        self.norm_factor =  max(self.value_perception) - min(self.value_perception) 
        self.comparison_clearness = comparison_clearness
        self.use_diff_levels = use_diff_levels

    def get_sorted(self, keys):
        user_order = list(keys)
        for i in range(1, len(user_order)):  

            val = user_order[i]
            j = i - 1  
            while j >= 0 and self.simulate_comparision([val, user_order[j]]):  
                
                user_order[j + 1] = user_order[j]  
                j -= 1

            user_order[j + 1] = val  

        diff_lvls = self.simulate_diff_levels(user_order)  

        return user_order, diff_lvls

    def simulate_diff_levels(self,keys):
        diff_lvls = np.full(len(keys)-1, DiffLevel.normal)
        if not self.use_diff_levels:
            return diff_lvls
        
        for i in range(len(diff_lvls)):
            mu_1 = self.value_perception[keys[i]]
            mu_2 = self.value_perception[keys[i+1]]
            overlap = NormalDist(mu_1,self.sigma).overlap(NormalDist(mu_2,self.sigma))
            r = random.random()
            if r < overlap:
                diff_lvls[i] = DiffLevel.none
                
            elif r < (((abs(mu_1 - mu_2)) ** (3/2)) / (self.norm_factor ** (3/2))):
                diff_lvls[i] = DiffLevel.major
                
        return diff_lvls


    def simulate_comparision(self, pair):
        val_1 = self.value_perception[pair[0]]
        val_2 = self.value_perception[pair[1]]

        gamma = np.log(abs(val_1-val_2) * self.comparison_clearness) / (2 * np.log(self.norm_factor * self.comparison_clearness))
        
        correct_prob = 1/2 + gamma

        if random.random() < correct_prob:
            return val_1 < val_2
        else:
            return val_1 >= val_2