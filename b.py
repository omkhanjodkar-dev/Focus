import win32con
import ctypes
import win32process
import customtkinter as tk
# from tkinter import messagebox
from CTkMessagebox import CTkMessagebox as ctkmsg
import win32gui

from test import Application

DWMWA_CLOAKED = 14
target = []
open_wins = {}

def button_press():
    if target != []:
        app = Application(target)
    else:
        ctkmsg(title='Warning', message='No windows selected for Focus.', icon='warning', sound=True)

def getWins(hwnd, ctx):
    cloaked = ctypes.c_int(0)
    ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))

    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd).strip() != "" and cloaked.value == 0 and not (ex_style & win32con.WS_EX_TOOLWINDOW):
        open_wins[win32gui.GetWindowText(hwnd)] = hwnd

def getWindows():
    win32gui.EnumWindows(getWins, None)

def select_func():
    getWindows()

    selection_box = tk.CTkToplevel(root)
    selection_box.title('Select Windows')
    selection_box.geometry(f'800x{100+len(open_wins)*30}')

    tk.CTkLabel(master=selection_box, text='Select all the windows that you want to be focused on/will need for the focus session.\nAll the window names in Green will be considered.\n', font=("", 20)).pack()

    buttons_frame = tk.CTkScrollableFrame(master=selection_box, orientation="vertical", width=700, height=len(open_wins)*30)
    buttons_frame.pack()

    def on_click(window, button):
        if button.cget('fg_color') == "green":
            target.remove(open_wins[window])
            button.configure(fg_color='black')
        else:
            target.append(open_wins[window])
            button.configure(fg_color="green")

    def get_bg(window):
        if open_wins[window] in target:
            return "green"
        return "black"

    def get_name(window):
        offset = 50
        if len(window) > offset:
            return window[0:offset-1] + " ..."
        return window

    window_buttons = []
    y = 0.05
    for window in open_wins:
        bg_clr = get_bg(window)
        nm = get_name(window)
        btn = tk.CTkButton(buttons_frame, text=nm, font=("Times New Roman", 20), fg_color=bg_clr)
        btn.configure(command=lambda w=window, b=btn: on_click(w, b))
        window_buttons.append(btn)
        # window_buttons[-1].place(relx=0.1, rely=y, anchor="w")
        window_buttons[-1].pack(fill="x")
        y+=0.95/len(open_wins)

    selection_box.grab_set()
    selection_box.focus_set()




root = tk.CTk()
root.title("Focus")
root.geometry("700x500")

tk.CTkLabel(root, text="Focus", font=("Times New Roman", 40)).place(relx=0.5, rely=0.2, anchor="center")
button = tk.CTkButton(root, text="ENTER", command=button_press, font=("Times New Roman", 20))
button.place(relx=2/7, rely=0.8, anchor="center")
select = tk.CTkButton(root, text="SELECT", command=select_func, font=("Times New Roman", 20))
select.place(relx=5/7, rely=0.8, anchor="center")

root.mainloop()