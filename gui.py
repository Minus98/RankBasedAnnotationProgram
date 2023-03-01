import customtkinter as ctk
from sorting_algorithms import *
from menu import MenuScreen
from ordering import OrderingScreen


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

        self.clear_screen()
        ordering_screen = OrderingScreen(
            self.root, save_obj, self.display_menu, self.center)
        ordering_screen.display()

    def center(self, w, h):
        # get screen width and height
        ws = self.root.winfo_screenwidth()  # width of the screen
        hs = self.root.winfo_screenheight()  # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2) - 40

        return x, y
