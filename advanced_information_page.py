from typing import Callable, Optional

import customtkinter as ctk


class AdvancedInformationPage():
    """
    Class representing the more advanced information pagewhich allows the user 
    to visualize more information regarding the algorithm
    """

    def __init__(
            self, root: ctk.CTk, menu_callback: Callable,
            initial_settings: Optional[dict] = None):
        """
        Initializes the AdvancedInformationPage instance.

        Args:
            root (CTk): The root cutom tkinter object.
            menu_callback (function): Callback function to return to the main 
            menu.
        """

        self.root = root
        self.menu_callback = menu_callback

        
