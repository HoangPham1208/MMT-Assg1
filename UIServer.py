import time
from tkinter import font
import re
from ServerAdmin import AdminManager
from P2PFetching import p2p_fetching_start
from PIL import Image, ImageTk
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


class FirstPage(Tk):
    def __init__(self):
        super().__init__()
        self.title("P2P FileSharing")
        self.geometry("800x500")

        # icon
        img = PhotoImage(file="Image/share.png")
        self.tk.call("wm", "iconphoto", self._w, img)

        # discover
        def discover():
            hname = host_nameEntry.get()
            if hname != "":
                result = []
                result = AdminManager.discover(self, hname)
                showList(result)
                self.close = True

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
            width=40,
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
        discoverBtn.place(x=300, y=90)

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

        self.mainloop()


if __name__ == "__main__":
    root = FirstPage()
