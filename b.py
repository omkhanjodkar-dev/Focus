import win32con
import ctypes
import win32process
import customtkinter as tk
# from tkinter import messagebox
from CTkMessagebox import CTkMessagebox as ctkmsg
import win32gui

from a import Application

class Software():
    def __init__(self):
        self.DWMWA_CLOAKED = 14
        self.target = []
        self.open_wins = {}

        self.root = tk.CTk()
        self.root.title("Focus")
        self.root.geometry("700x500")

        tk.CTkLabel(self.root, text="Focus", font=("Times New Roman", 40)).place(relx=0.5, rely=0.2, anchor="center")
        button = tk.CTkButton(self.root, text="ENTER", command=self.button_press, font=("Times New Roman", 20))
        button.place(relx=2/7, rely=0.8, anchor="center")
        self.root.update_idletasks()
        self.time_prompt = tk.CTkEntry(self.root, font=("Times New Roman", 20))
        self.time_prompt.place(relx=2/7, rely=0.8-(50/700+button.winfo_height()/700), anchor="center")
        select = tk.CTkButton(self.root, text="SELECT", command=self.select_func, font=("Times New Roman", 20))
        select.place(relx=5/7, rely=0.8, anchor="center")
        self.root.update_idletasks()
        select_prompt = tk.CTkEntry(self.root, font=("Times New Roman", 20))
        select_prompt.place(relx=5/7, rely=0.8-(50/700+select.winfo_height()/700), anchor="center")

        self.root.mainloop()


    def button_press(self):
        if self.target != [] and self.time_prompt.get().isdigit():
            app = Application(self.target, self.time_prompt.get())
        else:
            ctkmsg(title='Warning', message='No windows selected for Focus/Time prompt is incorrect.', icon='warning', sound=True)

    def getWins(self, hwnd, ctx):
        cloaked = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, self.DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))

        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd).strip() != "" and cloaked.value == 0 and not (ex_style & win32con.WS_EX_TOOLWINDOW):
            self.open_wins[win32gui.GetWindowText(hwnd)] = hwnd

    def getWindows(self):
        win32gui.EnumWindows(self.getWins, None)

    def select_func(self):
        # if select_box.get() != "":
        #     pass

        self.getWindows()

        selection_box = tk.CTkToplevel(self.root)
        selection_box.title('Select Windows')
        selection_box.geometry(f'800x{100+len(self.open_wins)*30}')

        tk.CTkLabel(master=selection_box, text='Select all the windows that you want to be focused on/will need for the focus session.\nAll the window names in Green will be considered.\n', font=("", 20)).pack()

        buttons_frame = tk.CTkScrollableFrame(master=selection_box, orientation="vertical", width=700, height=len(self.open_wins)*30)
        buttons_frame.pack()

        def on_click(window, button):
            if button.cget('fg_color') == "green":
                self.target.remove(self.open_wins[window])
                button.configure(fg_color='black')
            else:
                self.target.append(self.open_wins[window])
                button.configure(fg_color="green")

        def get_bg(window):
            if self.open_wins[window] in self.target:
                return "green"
            return "black"

        def get_name(window):
            offset = 50
            if len(window) > offset:
                return window[0:offset-1] + " ..."
            return window

        window_buttons = []
        y = 0.05
        for window in self.open_wins:
            bg_clr = get_bg(window)
            nm = get_name(window)
            btn = tk.CTkButton(buttons_frame, text=nm, font=("Times New Roman", 20), fg_color=bg_clr)
            btn.configure(command=lambda w=window, b=btn: on_click(w, b))
            window_buttons.append(btn)
            # window_buttons[-1].place(relx=0.1, rely=y, anchor="w")
            window_buttons[-1].pack(fill="x")
            y+=0.95/len(self.open_wins)

        selection_box.grab_set()
        selection_box.focus_set()



if "__main__" == __name__:
    software = Software()
