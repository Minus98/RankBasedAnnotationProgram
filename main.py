from sorting_algorithms import *
from pathlib import Path
from gui import TestGui
import random

img_paths = [str(path) for path in list(Path("Images").glob('*/*.jpg'))]
random.shuffle(img_paths)
c_sz = 2

sort_alg = MergeSort(img_paths)
gui = TestGui(sort_alg = sort_alg, comparison_size = c_sz)
gui.run()
