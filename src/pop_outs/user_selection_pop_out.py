import pickle
from pathlib import Path
from typing import Any, Callable

import customtkinter as ctk

import utils.ctk_utils as ctk_utils
import utils.saves_handler as saves_handler


class UserSelectionPopOut():
    """Class representing a pop-out window for user selection"""

    def __init__(self, root: ctk.CTk,
                 select_user_callback: Callable):
        """
        Initialize the UserSelectionPopOut.

        Args:
            root (CTk): The root window.
            select_user_callback (function): The callback function to select 
                                             a user.
        """

        self.root = root
        self.select_user_callback = select_user_callback

        self.pop_out = ctk.CTkToplevel()

        w = 500
        h = 700
        x, y = ctk_utils.center(self.root, w, h)

        self.pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.pop_out.columnconfigure(index=0, weight=1)
        self.pop_out.columnconfigure(index=1, weight=1)
        self.pop_out.rowconfigure(index=0, weight=1)
        self.pop_out.rowconfigure(index=1, weight=1)
        self.pop_out.rowconfigure(index=2, weight=1)

        path = Path(saves_handler.get_full_path('users.pickle'))
        if path.is_file():
            file = open(saves_handler.get_full_path("users.pickle"), 'rb')
            self.saved_users = pickle.load(file)
        else:
            self.saved_users = []

        label = ctk.CTkLabel(
            text="Who will be annotating this session?", master=self.pop_out,
            font=('Helvetica bold', 30),
            wraplength=400)
        label.grid(row=0, column=0, sticky='sew', columnspan=2, pady=10)

        self.saved_users_frame = ctk.CTkScrollableFrame(
            master=self.pop_out, height=400)

        self.saved_users_frame.grid(
            column=0, row=1, sticky="new", padx=20, columnspan=2)
        self.saved_users_frame.columnconfigure(0, weight=1)

        self.display_users()

        self.new_name_var = ctk.StringVar()

        self.new_name_var.trace_add("write", self.name_changed)

        self.user_entry = ctk.CTkEntry(
            self.pop_out, placeholder_text="Enter a new user", width=200,
            height=45, font=('Helvetica bold', 18),
            textvariable=self.new_name_var)
        self.user_entry.grid(column=0, row=2, sticky="ne", padx=(0, 5))
        self.user_entry.bind("<Return>", lambda event: self.on_return())

        self.new_button = ctk.CTkButton(
            master=self.pop_out, text="+", width=45, height=45,
            font=('Helvetica bold', 20),
            command=self.new_user, state=ctk.DISABLED)
        self.new_button.grid(column=1, row=2, sticky="nw")

        self.pop_out.grab_set()
        self.pop_out.attributes("-topmost", True)

    def display_users(self):
        """
        Display the saved users in the pop-out window.
        """

        for i, user in enumerate(self.saved_users):
            self.append_user_row(i, user)

    def append_user_row(self, i: int, user: str):
        """
        Append a user row to the saved users frame.

        Args:
            i (int): The row index.
            user (str): The user name.
        """

        saved_users_row = ctk.CTkFrame(
            master=self.saved_users_frame, fg_color=self.pop_out.cget(
                "fg_color"))

        saved_users_row.bind(
            "<Button-1>", command=lambda event: self.select_user(user))

        saved_users_row.grid(row=i, column=0, sticky="ew", pady=3)

        saved_users_row.grid_columnconfigure(0, weight=1, uniform="row")

        save_name_label = ctk.CTkLabel(
            master=saved_users_row, text=user, font=('Helvetica bold', 20))

        save_name_label.bind(
            "<Button-1>", command=lambda event: self.select_user(user))

        save_name_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")

        ctk_utils.add_hover(saved_users_row)

        delete_button = ctk.CTkLabel(
            master=saved_users_row, text="X", text_color="#C00000",
            font=('Helvetica bold', 20))
        delete_button.grid(row=0, column=1, padx=10, pady=4, sticky="e")
        delete_button.bind("<Enter>", lambda event,
                           widget=delete_button: widget.configure(
                               text_color="#F00000"))
        delete_button.bind("<Leave>", lambda event,
                           widget=delete_button: widget.configure(
                               text_color="#C00000"))

        delete_button.bind("<Button-1>", lambda event,
                           i=i: self.delete_user(i))

    def delete_user(self, i: int):
        """
        Delete a user from the saved users list.

        Args:
            i (int): The index of the user to delete.
        """
        self.saved_users.pop(i)

        f = open(saves_handler.get_full_path("users.pickle"), "wb")
        pickle.dump(self.saved_users, f)
        f.close()

        for child in self.saved_users_frame.winfo_children():
            child.grid_forget()

        self.display_users()

    def select_user(self, user: str):
        """
        Select a user and call the callback function.

        Args:
            user: The selected user.
        """
        self.select_user_callback(user)
        self.pop_out.destroy()

    def new_user(self):
        """
        Create a new user and update the saved users list.
        """

        name = self.new_name_var.get()

        self.saved_users.append(name)

        self.append_user_row(len(self.saved_users)-1, name)

        f = open(saves_handler.get_full_path("users.pickle"), "wb")
        pickle.dump(self.saved_users, f)
        f.close()

        self.new_name_var.set("")

    def name_changed(self, *args: Any):
        """
        Callback function for name changes. Enables or disables the new button 
        based on the validity of the name.

        Args:
            *args: Variable number of arguments.
        """

        if self.is_valid_name(self.new_name_var.get()):
            self.new_button.configure(state=ctk.NORMAL)
        else:
            self.new_button.configure(state=ctk.DISABLED)

    def is_valid_name(self, name: str) -> bool:
        """
        Check if the provided name is valid, i.e., not empty and not already 
        in the list of saved users.

        Args:
            name: The name to check.

        Returns:
            bool: True if the name is valid, False otherwise.
        """
        return name and name.lower() not in [
            user.lower() for user in self.saved_users]

    def on_return(self):
        """
        Callback function triggered when the Return key is pressed. 
        If the entered name is valid, it adds the new user.
        """
        if self.is_valid_name(self.new_name_var.get()):
            self.new_user()
