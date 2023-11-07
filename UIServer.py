import time
from tkinter import font
import re
from ServerAdmin import AdminManager
import tkinter as tk
import tkinter.ttk as ttk
import threading
import sys
import collections
from tkinter import *
from tkinter import Tk
import tkinter.messagebox
import tkinter.filedialog
import os


class Login(Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P FileSharing")
        self.geometry("450x500")
        self.configure(bg="#ffffff")

        def show():
            passwd.configure(show="")
            check.configure(command=hide, text="hide password")

        def hide():
            passwd.configure(show="*")
            check.configure(command=show, text="show password")

        label_0 = Label(
            self,
            fg="#57a1f8",
            bg="#fff",
            text="Login form",
            font=("Microsoft YaHei UI Light", 25, "bold"),
        )
        label_0.place(x=140, y=20)

        label_host = Label(self, text="Host name", bg="#fff", fg="#57a1f8")
        host = Entry(self, width=30, border=0)
        host.place(x=90, y=100)
        host.insert(0, "Hostname")
        host.bind("<FocusIn>", lambda event: on_enter(event, "host"))
        host.bind("<FocusOut>", lambda event: on_leave(event, "host"))
        Frame(self, width=295, height=2, bg="black").place(x=85, y=120)
        label_host.place(x=80, y=80)

        label_passwd = Label(self, text="Password", bg="#fff", fg="#57a1f8")
        passwd = Entry(self, width=30, border=0, show="*")
        passwd.place(x=90, y=150)
        passwd.insert(0, "HostPassword")
        passwd.bind("<FocusIn>", lambda event: on_enter(event, "passwd"))
        passwd.bind("<FocusOut>", lambda event: on_leave(event, "passwd"))
        label_passwd.place(x=80, y=130)

        check = Checkbutton(
            self, text="Show my password", bg="#fff", fg="#57a1f8", command=show
        )
        check.pack(side="top", pady=180)
        Frame(self, width=295, height=2, bg="black").place(x=85, y=170)

        submit = Button(
            self,
            text="Login",
            border=0,
            width=40,
            pady=5,
            bg="#57a1f8",
            fg="white",
            command=lambda: login_redirect(),
        )
        submit.place(x=90, y=220)

        def on_enter(_, name):
            if name == "host":
                host.delete(0, END)
            elif name == "passwd":
                passwd.delete(0, END)
            else:
                pass

        def on_leave(_, name):
            if name == "host":
                if host.get() == "":
                    host.insert(0, "Hostname")
            elif name == "passwd":
                if passwd.get() == "":
                    passwd.insert(0, "HostPassword")
            else:
                pass

        def login_redirect():
            # Validate results
            if host.get() == "" or host.get() == "Hostname":
                tkinter.messagebox.showerror(
                    title="Lỗi đăng nhập", message="Nhập host name !!"
                )
            elif passwd.get() == "" or passwd.get() == "HostPassword":
                tkinter.messagebox.showerror(
                    title="Lỗi đăng nhập", message="Nhập mật khẩu !!"
                )
            else:
                result = []
                result = AdminManager.login(self, host.get(), passwd.get())
                # move to OnlineUserPage
                if result == True:
                    self.close = True
                    HomePage()
                else:
                    tkinter.messagebox.showerror(
                        title="Lỗi đăng nhập",
                        message="Tài khoản hoặc mật khẩu không đúng!",
                    )

        self.mainloop()


class HomePage(Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P FileSharing")
        self.geometry("1000x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # discover
        def discover():
            hname = host_nameEntry.get()
            if hname != "":
                result = []
                result = AdminManager.discover(self, hname)
                showList(result)
                self.close = True

        # ping
        def ping():
            pname = host_nameEntryi.get()
            if pname != "":
                result = []
                result = AdminManager.ping(self, pname)
                print(result)
                listbox2.delete(0, tk.END)
                listbox2.insert(tk.END, result)
                self.close = True

        def updateListHostName():
            result = []
            result = AdminManager.showListHostname(self)
            listbox1.delete(0, tk.END)
            str = "        Host_name"
            listbox1.insert(tk.END, str)
            sub_list = result[1:]
            for item in sub_list:
                text = f"             {item}"
                listbox1.insert(tk.END, text)

        def showList(data):
            listbox.delete(0, tk.END)
            str = "Host_name                Port              File_name                      Date_added"
            listbox.insert(tk.END, str)
            for item in data:
                text = f"     {item['host_name']}                  {item['host_port']}               {item['file_name']}            {item['date_added']}"
                listbox.insert(tk.END, text)

        appTitle = tkinter.Label(
            self,
            text="P2P SERVER ADMIN",
            font=("Helvetica", 25, "bold"),
            width=50,
            background="#57a1f8",
            anchor="center",
        )
        appTitle.place(x=0, y=0)

        l1 = tkinter.Label(
            self,
            text="Discover:",
            font=("Helvetica", 11, "bold"),
        )
        l1.place(x=20, y=60)

        lb = tk.Label(self, text="Host_name:", font=("Helvetica", 11))
        lb.place(x=20, y=90)
        host_nameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        host_nameEntry.place(x=110, y=90)

        discoverBtn = Button(
            self,
            text="Discover",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=discover,
        )
        discoverBtn.place(x=650, y=90)

        list = tk.Frame(self, background="white")
        list.place(x=20, y=120)
        scroll = ttk.Scrollbar(list)
        listbox = tk.Listbox(
            list,
            yscrollcommand=scroll.set,
            font=("Helvetica", 14),
            width=65,
            height=10,
            selectbackground="#b8f89e",
            selectforeground="black",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            selectmode="single",
        )
        scroll.pack(side="right", fill="y")
        listbox.pack(side="left", padx=5, pady=5)

        listBtn = Button(
            self,
            text="Refresh",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=updateListHostName,
        )
        listBtn.place(x=880, y=90)

        list1 = tk.Frame(self, background="white")
        list1.place(x=800, y=120)
        scroll = ttk.Scrollbar(list1)
        listbox1 = tk.Listbox(
            list1,
            yscrollcommand=scroll.set,
            font=("Helvetica", 14),
            width=15,
            height=10,
            selectbackground="#b8f89e",
            selectforeground="black",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            selectmode="single",
        )
        scroll.pack(side="right", fill="y")
        listbox1.pack(side="left", padx=5, pady=5)
        ln = tkinter.Label(
            self,
            text="List Host Name:",
            font=("Helvetica", 11, "bold"),
        )
        ln.place(x=800, y=60)

        lpi = tkinter.Label(
            self,
            text="Ping:",
            font=("Helvetica", 11, "bold"),
        )
        lpi.place(x=20, y=360)

        lbi = tk.Label(self, text="Host_name:", font=("Helvetica", 11))
        lbi.place(x=20, y=390)
        host_nameEntryi = ttk.Entry(self, font=("Helvetica", 11), width=15)
        host_nameEntryi.place(x=110, y=390)

        pingBtn = Button(
            self,
            text="Ping",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=ping,
        )
        pingBtn.place(x=650, y=390)

        list2 = tk.Frame(self, background="white")
        list2.place(x=20, y=420)
        scroll = ttk.Scrollbar(list2)
        listbox2 = tk.Listbox(
            list2,
            yscrollcommand=scroll.set,
            font=("Helvetica", 14),
            width=65,
            height=10,
            selectbackground="#b8f89e",
            selectforeground="black",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            selectmode="single",
        )
        scroll.pack(side="right", fill="y")
        listbox2.pack(side="left", padx=5, pady=5)
        self.mainloop()

    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            os._exit(0)


if __name__ == "__main__":
    root = Login()
