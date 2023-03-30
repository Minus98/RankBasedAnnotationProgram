import sys
import os
from enum import Enum

class DiffLevel(Enum):
    none = 0
    normal = 1
    major = 2

def add_hover(widget):

    add_hover_to_children(widget, widget)


def add_hover_to_children(widget, child_widget):

    child_widget.bind("<Enter>", lambda event,
                      widget=widget, color=widget.cget("fg_color"): highlight(widget, color))
    child_widget.bind("<Leave>", lambda event,
                      widget=widget, color=widget.cget("fg_color"): remove_highlight(widget, color))

    for child in child_widget.winfo_children():
        add_hover_to_children(widget, child)


def highlight(widget, color):

    gray_color = int(color[1][-2:]) + 10

    if gray_color > 100:
        gray_color = 100

    widget.configure(fg_color='gray' + str((gray_color)))


def remove_highlight(widget, color):
    # might have to change so that it is recursive like highlight...
    widget.configure(fg_color=color)


def get_full_path(path):

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    path = application_path + "/" + path
    return path.replace("\\", "/")
