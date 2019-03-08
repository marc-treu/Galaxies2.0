import tkinter as tk


class InterfaceGalaxies(tk.Tk):


    def __init__(self):
        super().__init__()
        self.geometry("1200x600")
        #Frame.__init__(self, fenetre, width=768, height=576)
        #self.pack(fill=BOTH)
        self.paned_Window = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_Window.pack(side=tk.TOP, fill=tk.BOTH, pady=2, padx=2)
        self.paned_Window.add(tk.Label(self.paned_Window, text='Volet 1', anchor=tk.CENTER))
        self.paned_Window.add(tk.Label(self.paned_Window, text='Volet 2', anchor=tk.CENTER) )
        self.paned_Window.add(tk.Label(self.paned_Window, text='Volet 3', anchor=tk.CENTER) )
        self.paned_Window.pack()
        # Création de nos widgets


if __name__ == '__main__':
    interface = InterfaceGalaxies()

    interface.mainloop()
    interface.destroy()
