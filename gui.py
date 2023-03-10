import customtkinter as ctk
from pairwiseordering import PairwiseOrderingScreen
from sorting_algorithms import *
from menu import MenuScreen
from ordering import OrderingScreen
from user_selection_popout import UserSelectionPopOut

class TestGui():

    def __init__(self):

        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("dark-blue")

        self.root = ctk.CTk()

        w = 1300
        h = 720
        x, y = self.center(w, h)

        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.title("Rank-Based Annotation")

    def run(self):

        self.display_menu()

        UserSelectionPopOut(self.root, self.center, self.select_user)
        
        self.root.mainloop()

    def clear_screen(self):

        cols, rows = self.root.grid_size()

        # Reset the column and row configurations
        for i in range(cols):
            self.root.columnconfigure(i, weight=0)

        for i in range(rows):
            self.root.rowconfigure(i, weight=0)

        for child in self.root.winfo_children():
            child.destroy()

    def display_menu(self):

        self.clear_screen()
        menu_screen = MenuScreen(
            self.root, self.display_menu, self.display_ordering_screen, self.center)
        menu_screen.display()

    def display_ordering_screen(self, save_obj):

        if hasattr(self, 'selected_user'):
            self.clear_screen()

            if save_obj["sort_alg"].comparison_size == 2:
                ordering_screen = PairwiseOrderingScreen(
                    self.root, save_obj, self.display_menu, self.center, self.selected_user)
            else:
                ordering_screen = OrderingScreen(
                    self.root, save_obj, self.display_menu, self.center, self.selected_user)

            ordering_screen.display()
        else:
            UserSelectionPopOut(self.root, self.center, self.select_user)

    def center(self, w, h):
        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40

        return x, y

    def select_user(self, user):
        self.selected_user = user