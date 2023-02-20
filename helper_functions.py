from enum import Enum

def get_df_annotation(df, val_1,val_2):
    keys = df[val_2][val_1] # val_1 < val_2
    if len(keys) >= 3:
        diff = sum(keys) / len(keys)
        if diff <= 0.3:
            return [val_1,val_2]
        elif diff >= 0.6:
            return [val_2,val_1]
    return []

def update_data(ranked_list, df):
    comparisions = [[a, b] for idx, a in enumerate(ranked_list) for b in ranked_list[idx + 1:]]
    for [a, b] in comparisions:
        df[a][b].append(1) # a is larger than b
        df[b][a].append(0) # a is smaller than b

class DiffLevel(Enum):
    none = 0
    normal = 1
    major = 2