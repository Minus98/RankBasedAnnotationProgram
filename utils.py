import os
import sys
from enum import Enum
from typing import List

import customtkinter as ctk


class DiffLevel(Enum):
    none = 0
    normal = 1
    major = 2


def add_hover(widget: ctk.CTkWidget):
    """
    Add hover effect to the widget and its children.

    Args:
        widget (CTkWidget): The widget to add the hover effect to.
    """

    add_hover_to_children(widget, widget)


def add_hover_to_children(widget: ctk.CTkWidget, child_widget: ctk.CTkWidget):
    """
    Add hover effect to the child ctk widget and its children.

    Args:
        widget: The parent ctk widget.
        child_widget: The child ctk widget to add the hover effect to.
    """

    child_widget.bind("<Enter>", lambda event, widget=widget,
                      color=widget.cget("fg_color"): highlight(widget, color))
    child_widget.bind(
        "<Leave>", lambda event, widget=widget,
        color=widget.cget("fg_color"): remove_highlight(widget, color))

    for child in child_widget.winfo_children():
        add_hover_to_children(widget, child)


def highlight(widget: ctk.CTkWidget, og_color: List[str]):
    """
    Add highlight effect to the ctk widget by changing its foreground color.

    Args:
        widget: The ctk widget to highlight.
        color: The original foreground color of the widget.
    """
    gray_color = int(og_color[1][-2:]) + 10

    if gray_color > 100:
        gray_color = 100

    widget.configure(fg_color='gray' + str((gray_color)))


def remove_highlight(widget: ctk.CTkWidget, og_color: List[str]):
    """
    Remove highlight effect from the ctk widget by restoring its original foreground color.

    Args:
        widget: The ctk widget to remove the highlight effect from.
        color: The original foreground color of the widget.

    """
    widget.configure(fg_color=og_color)


def get_full_path(path: str) -> str:
    """
    Get the full path of a file or directory.

    Args:
        path: The relative path.

    Returns:
        str: The full path.
    """

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    path = application_path + "/" + path
    return path.replace("\\", "/")
