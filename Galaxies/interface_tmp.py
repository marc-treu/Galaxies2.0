import tkinter as tk 
from tkinter import messagebox
from tkinter import filedialog


fenetre = tk.Tk()
fenetre.geometry("500x500")
fenetre.title("Galaxy")


def open_text_align_file():
    filepath = filedialog.askopenfilename(title="Open a file",filetypes=[('tab files','.tab')])
    #ajout du code qui lance galaxy à partir du fichier .tab
    
    
def action2():
    messagebox.showinfo("alerte", "Bravo!")
    
def menu() :
    
    menubar = tk.Menu(fenetre)

    menu1 = tk.Menu(menubar,tearoff=0)
    menu1.add_command(label="With a text-align file", command=lambda:open_text_align_file())
    menu1.add_command(label="Compare 2 corpus", command=lambda:action2())
    menu1.add_separator()
    menu1.add_command(label="Quitter", command=fenetre.destroy)
    menubar.add_cascade(label="Start", menu=menu1)

    fenetre.config(menu=menubar)

menu()

fenetre.update()
p = tk.PanedWindow(fenetre, orient=tk.HORIZONTAL)
p.pack(side=tk.LEFT, expand="yes", fill=tk.BOTH, pady=2, padx=2)
p.add(tk.Label(p, text='Volet 1', background='blue', anchor=tk.CENTER), width = int(fenetre.winfo_width()/3))
p.add(tk.Label(p, text='Volet 2', background='white', anchor=tk.CENTER) ,width = int(fenetre.winfo_width()/3))
p.add(tk.Label(p, text='Volet 3', background='red', anchor=tk.CENTER),  width = int(fenetre.winfo_width()/3))
p.pack()
fenetre.update()
p.update()
fenetre.mainloop()
