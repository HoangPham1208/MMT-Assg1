import time
from tkinter import font
import re

# from CentralizedServer import CentralizedServer
# import P2PFetching
from Client import PeerManager
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk

# from tkinter import Image
import threading
import sys
import collections
from tkinter import *
from tkinter import Tk
import tkinter.messagebox
import tkinter.filedialog
import os


# First Page
class FirstPage(Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P FileSharing")
        self.geometry("450x500")
        self.configure(bg="#ffffff")

        # icon
        img = PhotoImage(file="Image/share.png")
        self.tk.call("wm", "iconphoto", self._w, img)

        # logo
        logo = PhotoImage(file="Image/logo.png")
        self.background = Label(self, width=400, height=188, image=logo).place(
            x=25, y=100
        )
        # self.background.pack()

        self.login = RegistryFrame(
            self,
            fname="login",
            bground="white",
        )
        self.register = RegistryFrame(self, fname="register", bground="white")

        # buttons
        buttonframe = Frame(self)
        buttonframe.pack(side="bottom")

        button1 = Button(
            buttonframe,
            border=0,
            width=20,
            pady=5,
            bg="#57a1f8",
            fg="white",
            text="Login",
            command=lambda: self.change_frame("login"),
        )
        button1.grid(row=0, column=0, padx=5, pady=5)
        button1.grid_rowconfigure(0, weight=1)
        button2 = Button(
            buttonframe,
            border=0,
            width=20,
            pady=5,
            bg="#57a1f8",
            fg="white",
            text="Register",
            comman=lambda: self.change_frame("register"),
        )
        button2.grid(row=0, column=1, padx=5, pady=5)

        self.mainloop()

    def change_frame(self, frame_name):
        if frame_name == "login":
            self.login.pack(fill="both", expand=1)
            self.register.pack_forget()
        elif frame_name == "register":
            self.register.pack(fill="both", expand=1)
            self.login.pack_forget()
        else:
            print("Ahuhu :((")

    # def auto_close(self):
    #     if self.login.close:
    #         self.login.close = -1  # stop sign
    #         self.destroy()

    #     elif self.login.close != -1:
    #         self.after(1000, self.auto_close)

    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.register.delete()
            self.login.delete()
            self.destroy()


#  Subframe for First Page - Toggle between Login and Register Service
class RegistryFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(bg=kwargs["bground"])
        self.fname = kwargs["fname"]
        self.close = False
        self.render()

    def delete(self):
        for widget in self.winfo_children():
            widget.destroy()

    def render(self):
        if self.fname == "login":
            label_0 = Label(
                self,
                fg="#57a1f8",
                bg="#fff",
                text="Login form",
                font=("Microsoft YaHei UI Light", 25, "bold"),
            )
            label_0.place(x=140, y=20)

            host = Entry(self, width=30, border=0)
            host.place(x=90, y=100)
            host.insert(0, "Hostname")
            host.bind("<FocusIn>", lambda event: on_enter(event, "host"))
            host.bind("<FocusOut>", lambda event: on_leave(event, "host"))
            Frame(self, width=295, height=2, bg="black").place(x=85, y=120)

            passwd = Entry(self, width=30, border=0)
            passwd.place(x=90, y=150)
            passwd.insert(0, "HostPassword")
            passwd.bind("<FocusIn>", lambda event: on_enter(event, "passwd"))
            passwd.bind("<FocusOut>", lambda event: on_leave(event, "passwd"))
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
                    result = PeerManager.login(self, host.get(), passwd.get())
                    # move to OnlineUserPage
                    if result == True:
                        self.close = True
                        hostn = host.get()
                        HomePage(hostn)
                    else:
                        tkinter.messagebox.showerror(
                            title="Lỗi đăng nhập",
                            message="Tài khoản hoặc mật khẩu không đúng!",
                        )

        elif self.fname == "register":
            label_0 = Label(
                self,
                fg="#57a1f8",
                bg="#fff",
                text="Registration form",
                font=("Microsoft YaHei UI Light", 25, "bold"),
            )
            label_0.place(x=80, y=20)

            host_name = Entry(self, width=30, border=0)
            host_name.place(x=80, y=100)
            host_name.insert(0, "Host name")
            host_name.bind("<FocusIn>", lambda event: on_enter(event, "host_name"))
            host_name.bind("<FocusOut>", lambda event: on_leave(event, "host_name"))
            Frame(self, width=295, height=2, bg="black").place(x=75, y=120)

            host_password = Entry(self, width=30, border=0)
            host_password.place(x=80, y=150)
            host_password.insert(0, "Host password")
            host_password.bind(
                "<FocusIn>", lambda event: on_enter(event, "host_password")
            )
            host_password.bind(
                "<FocusOut>", lambda event: on_leave(event, "host_password")
            )
            Frame(self, width=295, height=2, bg="black").place(x=75, y=170)

            re_host_password = Entry(self, width=30, border=0)
            re_host_password.place(x=80, y=200)
            re_host_password.insert(0, "Retype Host Password")
            re_host_password.bind(
                "<FocusIn>", lambda event: on_enter(event, "re_host_password")
            )
            re_host_password.bind(
                "<FocusOut>", lambda event: on_leave(event, "re_host_password")
            )
            Frame(self, width=295, height=2, bg="black").place(x=75, y=220)

            submit = Button(
                self,
                text="Register",
                border=0,
                width=40,
                pady=5,
                bg="#57a1f8",
                fg="white",
                command=lambda: register_redirect(),
            )
            submit.place(x=80, y=320)

            def on_enter(_, name):
                if name == "host_name":
                    host_name.delete(0, END)
                elif name == "host_password":
                    host_password.delete(0, END)
                elif name == "re_host_password":
                    re_host_password.delete(0, END)
                else:
                    pass

            def on_leave(_, name):
                if name == "host_name" and host_name.get() == "":
                    host_name.insert(0, "Host name")
                elif name == "host_password" and host_password.get() == "":
                    host_password.insert(0, "Host Password")
                elif name == "re_password" and re_host_password.get() == "":
                    re_host_password.insert(0, "Retype Host Password")
                else:
                    pass

            def register_redirect():
                # Validate results
                if host_name.get() == "" or host_name.get() == "Host name":
                    tkinter.messagebox.showerror(
                        title="Lỗi đăng kí", message="Vui lòng nhập host name !!"
                    )
                elif (
                    host_password.get() == "" or host_password.get() == "Host password"
                ):
                    tkinter.messagebox.showerror(
                        title="Lỗi đăng kí", message="Vui lòng nhập mật khẩu !!"
                    )
                elif not re.search(
                    "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$",
                    host_password.get(),
                ):
                    tkinter.messagebox.showerror(
                        title="Lỗi đăng kí",
                        message="Mật khẩu có độ dài tối thiểu là 6, bao gồm ít nhất 1 kí tự hoa, 1 kí tự thường, 1 chữ số và 1 kí tự đặc biệt (trừ khoảng trắng)",
                    )
                elif re_host_password.get() != host_password.get():
                    tkinter.messagebox.showerror(
                        title="Lỗi đăng kí",
                        message="Mật khẩu nhập lại không trùng khớp !!",
                    )
                else:
                    # CentralizedServer.sign_up(host_name.get(), host_password.get())
                    tkinter.messagebox.showinfo("Đăng kí", "Đăng kí thành công")
                    threading.Thread(
                        target=PeerManager.register(
                            self, host_name.get(), host_password.get()
                        ),
                        args=(host_name.get(), host_password.get()),
                    ).start()


class HomePage(Tk):
    def __init__(self, host):
        super().__init__()

        self.title("P2P FileSharing")
        self.geometry("650x500")
        self.configure(bg="#ffffff")

        # img1 = PhotoImage(file="Image/share.png")
        # self.iconphoto(False, img1)
        # icon
        # icon
        # không hiểu sao đoạn này cái icon nó bị lỗi

        def publishFile():
            fname = fnameEntry.get()
            lname = lnameEntry.get()
            if lname != "" and fname != "":
                PeerManager.publish(self, lname, fname)
                self.close = True
            else:
                tkinter.messagebox.showerror("Error", "Missing value")

        def fetchFile():
            filename = filenameEntry.get()
            peer = peerportEntry.get()
            if filename != "" and peer != "":
                PeerManager.publish(self, filename, peer)
                self.close = True
            else:
                tkinter.messagebox.showerror("Error", "Missing value")

        appTitle = tkinter.Label(
            self,
            text="P2P FILESHARING APP",
            font=("Helvetica", 25, "bold"),
            width=33,
            background="#57a1f8",
            anchor="center",
        )
        appTitle.place(x=0, y=0)

        l1 = tkinter.Label(self, text="Host_name:", font=("Helvetica", 11))
        l1.place(x=20, y=60)
        # host_name = host
        # l1 = tkinter.Label(self, text=host_name, font=("Helvetica", 11))
        # l1.place(x=120, y=60)

        # Publish
        l3 = tk.Label(self, text="Publish File:", font=("Helvetica", 11))
        l3.place(x=20, y=110)
        l4 = tk.Label(self, text="lname:", font=("Helvetica", 11))
        l5 = tk.Label(self, text="file_name:", font=("Helvetica", 11))
        l4.place(x=20, y=140)
        l5.place(x=230 + 50, y=140)
        lnameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        fnameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        lnameEntry.place(x=100, y=140)
        fnameEntry.place(x=370, y=140)
        publishBtn = ttk.Button(
            self,
            text="Publish",
            style="my.TButton",
            width=12,
            takefocus=0,
            command=publishFile,
        )
        publishBtn.place(x=555, y=140)

        # Fetch

        la = tk.Label(self, text="Fetch File:", font=("Helvetica", 11))
        la.place(x=20, y=380)
        lb = tk.Label(self, text="file_name:", font=("Helvetica", 11))
        lc = tk.Label(self, text="peer_port:", font=("Helvetica", 11))
        lb.place(x=20, y=410)
        lc.place(x=230 + 50, y=410)
        filenameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        peerportEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        filenameEntry.place(x=100, y=410)
        peerportEntry.place(x=370, y=410)
        fetchBtn = ttk.Button(
            self,
            text="Fetch",
            style="my.TButton",
            width=12,
            takefocus=0,
            command=fetchFile,
        )
        fetchBtn.place(x=555, y=410)
        self.mainloop()


if __name__ == "__main__":
    root = FirstPage()
