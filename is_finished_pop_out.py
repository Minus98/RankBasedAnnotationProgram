import customtkinter as ctk


class IsFinishedPopOut():

    def __init__(self, root, center, back_to_menu):

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

        label = ctk.CTkLabel(text="Hello! \n You are now done annotating thank you very much. \n What do you want to do next?",
                             master=pop_out, font=('Helvetica bold', 30))
        label.grid(row=0, column=0, sticky='nsew', columnspan=2)

        menu_button = ctk.CTkButton(
            text="Return to menu", command=self.back_to_menu, width=w//2-20, height=h//5, master=pop_out, font=('Helvetica bold', 30))
        menu_button.grid(row=1, column=0, sticky='sew',
                         pady=(0, 10), padx=(10, 5))
        quit_button = ctk.CTkButton(text="Quit", command=self.root.destroy,
                                    width=w//2-20, height=h//5, master=pop_out, font=('Helvetica bold', 30))
        quit_button.grid(row=1, column=1, sticky='sew',
                         pady=(0, 10), padx=(5, 10))

        pop_out.grab_set()
