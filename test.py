# Try to import Python 2 name
try:
    import Tkinter as tk
# Fall back to Python 3 if import fails
except ImportError:
    import tkinter as tk

class Example(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        menubar = tk.Menu(self)
        fileMenu = tk.Menu(self)
        recentMenu = tk.Menu(self)

        menubar.add_cascade(label="File", menu=fileMenu)
        fileMenu.add_cascade(label="Open Recent", menu=recentMenu)
        for name in ("file1.txt", "file2.txt", "file3.txt"):
            recentMenu.add_command(label=name)


        root.configure(menu=menubar)
        root.geometry("200x200")

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()