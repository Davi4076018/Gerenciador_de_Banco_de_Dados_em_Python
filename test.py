from tkinter import ttk
import tkinter as tk

# Creating tkinter my_w
my_w = tk.Tk()
my_w.geometry("480x280")
my_w.title("www.plus2net.com")
# Using treeview widget
font1 = ['Times', 12, 'normal']
style = ttk.Style(my_w)
style.theme_use("clam")  # set theam to clam
style.configure("Treeview", background="black",
                fieldbackground="black", foreground="white", font=font1)
style.configure('Treeview.Heading', background="PowderBlue")

trv = ttk.Treeview(my_w, selectmode='browse')
trv.grid(row=1, column=1, rowspan=5, padx=5, pady=20)
# number of columns
trv["columns"] = ("1")
# Defining heading
trv['show'] = 'tree headings'
# trv['show'] = 'tree'

# width of columns and alignment
trv.column("#0", width=90, anchor='w')
trv.column("1", width=130, anchor='w')

# Headings
# respective columns
trv.heading("#0", text="#")
trv.heading("1", text="Name")
trv.insert("", 'end', iid='a', open=True, values=('na-Alex'))
trv.insert("", 'end', iid=1, open=True, text='1', values=('n1-Alex'))
trv.insert("1", 'end', iid='1c', open=True, text='1c', values=('Child-Alex'))
trv.insert("", 'end', iid=2, open=True, text=2, values=('Ron'))
trv.insert("2", 'end', iid='2c', open=False, text='2c', values=('Child-Ron'))
trv.insert("2c", 'end', iid='2cc', open=True, text='2cc', values=('Child2-Ron'))


def data_collect(self):
    p_id = trv.selection()[0]  # collect selected row id
    e1_str.set(p_id)


def data_insert():
    print(e4_str.get())
    if (e2_str.get() == ''):
        trv.insert(e1_str.get(), 'end', open=True,
                   text=e3_str.get(), values=(e4_str.get(),))
    else:
        trv.insert(e1_str.get(), 'end', iid=e2_str.get(), open=True,
                   text=e3_str.get(), values=(e4_str.get(),))
    e1_str.set('')
    e2_str.set('')
    e3_str.set('')
    e4_str.set('')


trv.bind("<<TreeviewSelect>>", data_collect)  # on select event
l1 = tk.Label(my_w, text='Parent Id', width=10)
l1.grid(row=1, column=2)
e1_str = tk.StringVar(my_w)
e1 = tk.Entry(my_w, textvariable=e1_str, bg='yellow', width=15, font=16)
e1.grid(row=1, column=3)

l2 = tk.Label(my_w, text='iid', width=10)
l2.grid(row=2, column=2)
e2_str = tk.StringVar(my_w)
e2 = tk.Entry(my_w, textvariable=e2_str, bg='yellow', width=15, font=16)
e2.grid(row=2, column=3)

l3 = tk.Label(my_w, text='text', width=10, font=16)
l3.grid(row=3, column=2)
e3_str = tk.StringVar(my_w)
e3 = tk.Entry(my_w, textvariable=e3_str, bg='yellow', width=15, font=16)
e3.grid(row=3, column=3)

l4 = tk.Label(my_w, text='values', width=10)
l4.grid(row=4, column=2)
e4_str = tk.StringVar(my_w)
e4 = tk.Entry(my_w, textvariable=e4_str, bg='yellow', width=15, font=16)
e4.grid(row=4, column=3)
b1 = tk.Button(my_w, text='Insert', command=lambda: data_insert())
b1.grid(row=5, column=2)

my_w.mainloop()