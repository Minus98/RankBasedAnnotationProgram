from sorting_algorithms import *
from pathlib import Path
from gui import TestGui
import random
import pickle

img_paths = [str(path) for path in list(Path("Images").glob('*/*.jpg'))]
random.shuffle(img_paths)
c_sz = 2

saved_state_path = Path('state.pickle')

if saved_state_path.is_file():
    file = open(saved_state_path, 'rb')
    sort_alg = pickle.load(file)
else:
    sort_alg = TrueSkill(img_paths)

gui = TestGui(sort_alg=sort_alg, comparison_size=c_sz)
gui.run()
