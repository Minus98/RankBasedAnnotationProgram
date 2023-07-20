import sys
from typing import Optional, Tuple

import customtkinter as ctk

from advanced_creation_menu import AdvancedCreationMenu
from menu import MenuScreen
from multiordering import MultiOrderingScreen
from pairwiseordering import PairwiseOrderingScreen
from rating import RatingScreen
from sorting_algorithms import HybridTrueSkill, RatingAlgorithm
from user_selection_pop_out import UserSelectionPopOut


class AnnotationGui():
    """
    Annotation GUI class for the Rank-Based Annotation application.
    """

    def __init__(self):
        """
        Initializes the AnnotationGui object.
        """

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()

        w = 1500
        h = 830
        x, y = self.center(w, h)

        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.title("Rank-Based Annotation")

        if sys.platform == "linux" or sys.platform == "linux2":
            self.root.attributes('-zoomed', True)

    def run(self):
        """
        Runs the Annotation GUI application.
        """

        self.display_menu()

        UserSelectionPopOut(self.root, self.center, self.select_user)

        self.root.mainloop()

    def clear_screen(self):
        """
        Clears the screen by destroying all child widgets and resetting column 
        and row configurations.
        """

        cols, rows = self.root.grid_size()

        # Reset the column and row configurations
        for i in range(cols):
            self.root.columnconfigure(i, weight=0)

        for i in range(rows):
            self.root.rowconfigure(i, weight=0)

        for child in self.root.winfo_children():
            child.destroy()

    def display_menu(self):
        """
        Displays the menu screen.
        """

        self.clear_screen()
        self.menu_screen = MenuScreen(
            self.root, self.display_menu, self.display_ordering_screen, self.
            center, self.open_user_selection, self.display_advanced_creation_menu)
        if hasattr(self, 'selected_user'):
            self.menu_screen.display_user(self.selected_user)
        self.menu_screen.display()

    def display_advanced_creation_menu(
            self, initial_settings: Optional[dict] = None):
        """
        Displays the advanced creation menu.

        Args:
            initial_settings (Optional[dict]): Dictionary containing initial values 
                                               for fields in the creation menu.
        """

        self.clear_screen()

        self.advanced_creation_menu = AdvancedCreationMenu(
            self.root, self.display_menu, initial_settings)

        self.advanced_creation_menu.display()

    def display_ordering_screen(self, save_obj: dict,
                                hybrid_transition_made: bool = False):
        """
        Displays the ordering screen based on the selected sort algorithm.

        Args:
            save_obj (dict): The save object containing the sort algorithm and 
            other parameters.
            hybrid_transition_made (bool): A boolean indicating if a hybrid 
            transition has been made.
        """

        if hasattr(self, 'selected_user'):
            self.clear_screen()

            sort_alg = save_obj["sort_alg"]
            if type(sort_alg) == HybridTrueSkill:
                sort_alg = sort_alg.sort_alg

            if type(sort_alg) == RatingAlgorithm:
                ordering_screen = RatingScreen(
                    self.root, save_obj, self.display_menu, self.center, self.
                    selected_user, self.reload_ordering_screen,
                    hybrid_transition_made)

            elif sort_alg.comparison_size == 2:
                ordering_screen = PairwiseOrderingScreen(
                    self.root, save_obj, self.display_menu, self.center, self.
                    selected_user, self.reload_ordering_screen)

            else:
                ordering_screen = MultiOrderingScreen(
                    self.root, save_obj, self.display_menu, self.center, self.
                    selected_user, self.reload_ordering_screen)

            if ordering_screen.image_directory_located:
                ordering_screen.display()
        else:
            UserSelectionPopOut(self.root, self.center, self.select_user)

    def center(self, w: int, h: int) -> Tuple[int, int]:
        """
        Calculates the x and y coordinates to center the Tk root window.

        Args:
            w (int): The width of the window.
            h (int): The height of the window.

        Returns:
            The x and y coordinates to center the window.
        """

        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40

        return x, y

    def select_user(self, user: str):
        """
        Selects a user and updates the selected user in the menu screen.

        Args:
            user (str): The selected user.
        """
        self.selected_user = user
        self.menu_screen.display_user(user)

    def open_user_selection(self):
        """
        Opens the user selection pop-up.
        """
        UserSelectionPopOut(self.root, self.center, self.select_user)

    def reload_ordering_screen(self, save_obj: dict):
        """
        Reloads the ordering screen with the updated save object.

        Args:
            save_obj (dict): The updated save object.
        """
        self.display_ordering_screen(save_obj, hybrid_transition_made=True)
