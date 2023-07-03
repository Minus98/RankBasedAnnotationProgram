from typing import Callable

import customtkinter as ctk


class IsFinishedPopOut():
    """
    Pop-out window for indicating the annotation status in the Rank-Based 
    Annotation application.
    """

    def __init__(
            self, root: ctk.CTk, center: Callable, back_to_menu: Callable,
            state: str = 'finished'):
        """
        Initializes the IsFinishedPopOut object.

        Args:
            root (CTk): The root cutom tkinter object.
            center (function): A function to center the pop-out window.
            back_to_menu (function): A function to go back to the main menu.
            state (str): The state of the annotation, either 'finished' or 'not finished'.
        """

        self.root = root
        self.center = center
        self.back_to_menu = back_to_menu

        pop_out = ctk.CTkToplevel()

        w = 700
        h = 300
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)

        if state == 'finished':
            label = ctk.CTkLabel(
                text="You are now done annotating, thank you very much!" +
                "\n What do you want to do next?", master=pop_out,
                font=('Helvetica bold', 26))
        else:
            label = ctk.CTkLabel(
                text="You have now done all your possible annotations!" +
                "\n What do you want to do next?", master=pop_out,
                font=('Helvetica bold', 26))

        label.grid(row=0, column=0, sticky='nsew', columnspan=2)

        menu_button = ctk.CTkButton(
            text="Return to menu", command=self.back_to_menu, width=w // 2 - 20,
            height=h // 5, master=pop_out, font=('Helvetica bold', 30))
        menu_button.grid(row=1, column=0, sticky='sew',
                         pady=(0, 10), padx=(10, 5))
        quit_button = ctk.CTkButton(
            text="Quit", command=self.root.destroy, width=w // 2 - 20, height=h
            // 5, master=pop_out, font=('Helvetica bold', 30))
        quit_button.grid(row=1, column=1, sticky='sew',
                         pady=(0, 10), padx=(5, 10))

        pop_out.protocol("WM_DELETE_WINDOW", self.back_to_menu)

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)
