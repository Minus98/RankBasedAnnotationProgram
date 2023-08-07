import os
from typing import Callable

import customtkinter as ctk

import utils.saves_handler as saves_handler


class DeletePopOut():
    """
    Pop-out window to confirm the deletion of an annotation save.
    """

    def __init__(
            self, root: ctk.CTk, center: Callable, deletion_callback: Callable,
            save_obj: dict):
        """
        Initializes the DeletePopOut object.

        Args:
            root (CTk): The root cutom tkinter object.
            center (function): A function to center the pop-out window.
            deletion_callback (function): A function to refresh the main menu.
            save_obj (dict): The save object that is up for deletion.
        """

        self.root = root
        self.center = center
        self.deletion_callback = deletion_callback
        self.save_obj = save_obj

        pop_out = ctk.CTkToplevel()

        w = 700
        h = 300
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)

        label = ctk.CTkLabel(
            text="Do you really wish to delete " + save_obj["name"] + "?" +
            "\n This action cannot be undone.", master=pop_out,
            font=('Helvetica bold', 26))

        label.grid(row=0, column=0, sticky='nsew', columnspan=2)

        delete_button = ctk.CTkButton(
            text="Delete", command=self.delete_save, fg_color="#ed022a",
            hover_color="#bf0021", width=w // 2 - 20, height=h // 5,
            master=pop_out, font=('Helvetica bold', 30))
        delete_button.grid(row=1, column=0, sticky='sew',
                           pady=(0, 10), padx=(10, 5))
        cancel_button = ctk.CTkButton(
            text="Cancel", command=pop_out.destroy, width=w // 2 - 20,
            height=h // 5, master=pop_out, font=('Helvetica bold', 30))
        cancel_button.grid(row=1, column=1, sticky='sew',
                           pady=(0, 10), padx=(5, 10))

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)

    def delete_save(self):
        """
        Deletes the .csv and .pickle files associated with the save object.
        Refreshes menu and destroys pop out.
        """

        path = saves_handler.get_path_to_save(self.save_obj)

        # Should the csv file be kept?
        os.remove(path + ".csv")
        os.remove(path + ".pickle")

        self.deletion_callback()
