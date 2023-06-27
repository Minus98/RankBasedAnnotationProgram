import json

import customtkinter as ctk


class SwitchingModesPopOut():

    def __init__(self, root, center):

        self.root = root
        self.center = center

        pop_out = ctk.CTkToplevel()

        w = 700
        h = 300
        x, y = self.center(w, h)

        pop_out.geometry('%dx%d+%d+%d' % (w, h, x, y))
        pop_out.columnconfigure(index=0, weight=1)
        pop_out.columnconfigure(index=1, weight=1)
        pop_out.rowconfigure(index=0, weight=1)
        pop_out.rowconfigure(index=1, weight=1)

        with open('prompts.json', 'r') as file:
            prompts = json.load(file)

        label = ctk.CTkLabel(
            text=prompts['finished_rating'],
            master=pop_out, font=('Helvetica bold', 26))

        label.grid(row=0, column=0, sticky='nsew', columnspan=2)

        menu_button = ctk.CTkButton(
            text="Ok", command=pop_out.destroy, width=w // 2 - 20, height=h //
            5, master=pop_out, font=('Helvetica bold', 30))
        menu_button.grid(row=1, column=0, sticky='s',
                         pady=(0, 10), padx=10, columnspan=2)

        pop_out.grab_set()
        pop_out.attributes("-topmost", True)
