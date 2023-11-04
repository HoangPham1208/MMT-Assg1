import re
from Client import PeerManager
from P2PFetching import p2p_fetching_start
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
import threading
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
        self.after(1000, lambda: self.auto_close())

        self.login = RegistryFrame(self, fname="login", bground="white")
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

    def auto_close(self):
        if self.login.close:
            self.login.close = -1  # stop sign
            self.destroy()
        elif self.login.close != -1:
            self.after(1000, self.auto_close)


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
                        peer_port = self.peer_port
                        hostn = host.get()
                        p2p_fetching_start("localhost", peer_port)
                        HomePage(hostn, peer_port)
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
    def __init__(self, host, peer_port):
        super().__init__()
        self.peer_port = peer_port
        self.title("P2P FileSharing")
        self.geometry("660x500")
        # self.configure(bg="#ffffff")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        def publishFile():
            fname = fnameEntry.get()
            lname = lnameEntry.get()
            if lname != "" and fname != "":
                # # check
                # repo_path = os.path.join(os.getcwd(), "repo_2")
                # repo_path = repo_path.replace(os.path.sep, "/")
                # # if not os.path.exists(repo_path):

                # # false
                PeerManager.publish(self, lname, fname)
                # true -> popup -> ???
                self.close = True
                tkinter.messagebox.showinfo(
                    "Successfully published", "Successfully published"
                )
            else:
                tkinter.messagebox.showerror("Error", "Missing value")

        def searchFile():
            fname1 = file_nameEntry.get()
            if fname1 != "":
                result = []
                result = PeerManager.search(self, fname1)
                showListPeer(result)
                self.close = True

        def updateListFile():
            result = []
            result = PeerManager.refresh(self, host_name)
            listbox1.delete(0, tk.END)
            str = "            File_name"
            listbox1.insert(tk.END, str)
            for item in result:
                if item["host_name"] == host_name:
                    text = f"              {item['file_name']} "
                    listbox1.insert(tk.END, text)

        def showListPeer(data):
            listbox.delete(0, tk.END)
            str = "Host_name       Port       File_name"
            listbox.insert(tk.END, str)
            for item in data:
                text = f"   {item['host_name']}           {item['host_port']}        {item['file_name']}"
                listbox.insert(tk.END, text)

        def fetchFile():
            filename = filenameEntry.get()
            peer_port = int(peerportEntry.get())
            if filename != "" and peer_port != "":
                PeerManager.fetch(self, filename, peer_port)
                self.close = True
                tkinter.messagebox.showinfo(
                    "Successfully fetched", "Successfully fetched"
                )

            else:
                tkinter.messagebox.showerror("Error", "Missing value")

        #
        appTitle = tkinter.Label(
            self,
            text="P2P FILESHARING APP",
            font=("Helvetica", 25, "bold"),
            width=33,
            background="#57a1f8",
            anchor="center",
        )
        appTitle.place(x=0, y=0)

        l1 = tkinter.Label(
            self,
            text="Host_name:",
            font=("Helvetica", 11, "bold"),
        )
        l1.place(x=20, y=60)
        host_name = host
        l2 = tkinter.Label(self, text=host_name, font=("Helvetica", 11))
        l2.place(x=120, y=60)

        # port
        lp = tk.Label(self, text="Port:", font=("Helvetica", 11, "bold"))
        lp.place(x=200, y=60)
        lp1 = tk.Label(self, text=self.peer_port, font=("Helvetica", 11))
        lp1.place(x=250, y=60)
        # Publish
        l3 = tk.Label(self, text="Publish File:", font=("Helvetica", 11, "bold"))
        l3.place(x=20, y=110)
        l4 = tk.Label(self, text="lname:", font=("Helvetica", 11))
        l5 = tk.Label(self, text="file_name:", font=("Helvetica", 11))
        l4.place(x=20, y=140)
        l5.place(x=280, y=140)
        lnameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        fnameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        lnameEntry.place(x=100, y=140)
        fnameEntry.place(x=370, y=140)

        publishBtn = Button(
            self,
            text="Publish",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=publishFile,
        )
        publishBtn.place(x=555, y=140)

        # search
        la = tk.Label(self, text="Search File:", font=("Helvetica", 11, "bold"))
        la.place(x=20, y=180)
        lb = tk.Label(self, text="file_name:", font=("Helvetica", 11))
        lb.place(x=20, y=210)
        file_nameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        file_nameEntry.place(x=100, y=210)

        searchFileBtn = Button(
            self,
            text="Search",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=searchFile,
        )
        searchFileBtn.place(x=240, y=210)
        # search -> list
        fileArea = tk.Frame(self, background="white")
        fileArea.place(x=20, y=240)
        scroll = ttk.Scrollbar(fileArea)
        listbox = tk.Listbox(
            fileArea,
            yscrollcommand=scroll.set,
            font=("Helvetica", 14),
            width=28,
            height=5,
            selectbackground="#b8f89e",
            selectforeground="black",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            selectmode="single",
        )
        scroll.pack(side="right", fill="y")
        listbox.pack(side="left", padx=5, pady=5)

        # List File
        lf = tk.Label(self, text="List File:", font=("Helvetica", 11))
        lf.place(x=400, y=180)
        showListFile = Button(
            self,
            text="Refresh",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=updateListFile,
        )
        showListFile.place(x=555, y=180)
        listfile = tk.Frame(self, background="white")
        listfile.place(x=400, y=240)
        scroll = ttk.Scrollbar(listfile)
        listbox1 = tk.Listbox(
            listfile,
            yscrollcommand=scroll.set,
            font=("Helvetica", 14),
            width=20,
            height=5,
            selectbackground="#b8f89e",
            selectforeground="black",
            activestyle="none",
            highlightthickness=0,
            borderwidth=0,
            selectmode="single",
        )
        scroll.pack(side="right", fill="y")
        listbox1.pack(side="left", padx=5, pady=5)

        # Fetch
        la = tk.Label(self, text="Fetch File:", font=("Helvetica", 11, "bold"))
        la.place(x=20, y=380)
        lb = tk.Label(self, text="file_name:", font=("Helvetica", 11))
        lc = tk.Label(self, text="peer_port:", font=("Helvetica", 11))
        lb.place(x=20, y=410)
        lc.place(x=230 + 50, y=410)
        filenameEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        peerportEntry = ttk.Entry(self, font=("Helvetica", 11), width=15)
        filenameEntry.place(x=100, y=410)
        peerportEntry.place(x=370, y=410)
        fetchBtn = Button(
            self,
            text="Search",
            border=1,
            width=12,
            bg="#57a1f8",
            fg="black",
            command=fetchFile,
        )
        fetchBtn.place(x=555, y=410)

        self.mainloop()

    def on_closing(self):
        if tkinter.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            os._exit(0)


if __name__ == "__main__":
    root = FirstPage()


# def show_popup():
#     response = messagebox.askquestion("Question", "Do you want to Rename?")
#     if response == "yes":
#         print("User chose 'Yes'")
#     else:
#         print("User chose 'No'")
