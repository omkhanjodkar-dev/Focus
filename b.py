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
        self.time_target = 0

        self.root = tk.CTk()
        self.root.title("Focus")
        self.root.geometry("700x500")

        self.go_label = tk.CTkLabel(self.root, text="Ready to Go?", font=("", 30))
        self.go_label.place(relx=1/2, rely=1/3, anchor="center")
        self.start_button = tk.CTkButton(self.root, text="START", font=("", 30), command=self.scene2)
        self.start_button.place(relx=1/2, rely=2/3, anchor="center")

        # tk.CTkLabel(self.root, text="Focus", font=("Times New Roman", 40)).place(relx=0.5, rely=0.2, anchor="center")
        # button = tk.CTkButton(self.root, text="ENTER", command=self.button_press, font=("Times New Roman", 20))
        # button.place(relx=2/7, rely=0.8, anchor="center")
        # self.root.update_idletasks()
        # self.time_prompt = tk.CTkEntry(self.root, font=("Times New Roman", 20))
        # self.time_prompt.place(relx=2/7, rely=0.8-(50/700+button.winfo_height()/700), anchor="center")
        # select = tk.CTkButton(self.root, text="SELECT", command=self.select_func, font=("Times New Roman", 20))
        # select.place(relx=5/7, rely=0.8, anchor="center")
        # self.root.update_idletasks()
        # select_prompt = tk.CTkEntry(self.root, font=("Times New Roman", 20))
        # select_prompt.place(relx=5/7, rely=0.8-(50/700+select.winfo_height()/700), anchor="center")

        self.root.mainloop()

    def scene2(self):
        self.go_label.destroy()
        self.start_button.destroy()

        self.time_label = tk.CTkLabel(self.root, text="How much time do we study for?", font=("", 30))
        self.time_label.place(relx=1/2, rely=1/4, anchor="center")
        self.time_info = tk.CTkLabel(self.root, text="Minutes:", font=("", 15))
        self.time_info.place(relx=1/2, rely=2.5/5, anchor="center")
        self.time_entry = tk.CTkEntry(self.root, font=("", 30), justify="center",)
        # self.time_entry._CTkEntry__placeholder_text_label.configure(font=("", 25))
        self.time_entry.place(relx=1/2, rely=2.8/5, anchor="center")
        self.time_warn = tk.CTkLabel(self.root, font=("", 15), text="", text_color="red")
        self.time_warn.place(relx=1/2, rely=3.2/5, anchor="center")
        self.time_button = tk.CTkButton(self.root, text="Go ahead!", font=("", 30), command=self.scene3)
        self.time_button.place(relx=1/2, rely=3/4, anchor="center")

        self.root.update()
        self.root.update_idletasks()

    def scene3(self):
        try:
            self.time_target = int(self.time_entry.get())
        except Exception as e:
            self.time_warn.configure(text="Please enter the time correctly.")
            return

        self.getWindows()

        self.time_label.destroy()
        self.time_info.destroy()
        self.time_entry.destroy()
        self.time_button.destroy()
        self.time_warn.destroy()


        self.window_label = tk.CTkLabel(self.root, text="What windows do we focus on?", font=("", 30))
        self.window_label.place(relx=1/2, rely=1/5, anchor="center")
        self.window_info = tk.CTkLabel(self.root, text="Select all the windows that you want to focus on.", font=("", 15))
        self.window_info.place(relx=1/2, rely=1.5/5, anchor="center")
        self.scroll_frame = tk.CTkScrollableFrame(master=self.root, orientation="vertical", width=250, height=120)

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
            btn = tk.CTkButton(self.scroll_frame, text=nm, font=("Times New Roman", 21), fg_color=bg_clr)
            btn.configure(command=lambda w=window, b=btn: on_click(w, b))
            window_buttons.append(btn)
            # window_buttons[-1].place(relx=0.1, rely=y, anchor="w")
            window_buttons[-1].pack(fill="x", pady=1)
            y+=0.95/len(self.open_wins)
            # tk.CTkLabel(self.scroll_frame, text="", font=("", 1)).pack(fill="x")

        def back_enter(event):
            self.back.configure(font=("", 37))

        def back_leave(event):
            self.back.configure(font=("", 30))


        self.scroll_frame.place(relx=1/2, rely=1.1/2, anchor="center")
        self.window_warn = tk.CTkLabel(self.root, text="", font=("", 15), text_color="red")
        self.window_warn.place(relx=1/2, rely=4/5, anchor="center")
        self.window_button = tk.CTkButton(self.root, text="Confirmed!", font=("", 30), command=self.scene4)
        self.window_button.place(relx=1/2, rely=4.4/5, anchor="center")
        self.back = tk.CTkButton(self.root, text="←", font=("Segoe UI Semibold", 30), text_color=self.window_button.cget("fg_color"), fg_color=self.root.cget("fg_color"), hover_color=self.root.cget("fg_color"))
        self.back.place(relx=0.08, rely=0.08, anchor="center")

        self.back.bind("<Enter>", back_enter, add="+")
        self.back.bind("<Leave>", back_leave, add="+")

        self.root.update()
        self.root.update_idletasks()

    def scene4(self):
        if self.target == []:
            self.window_warn.configure(text="Select atleast 1 window for Focus.")
            return

        self.window_label.destroy()
        self.window_info.destroy()
        self.scroll_frame.place_forget()
        # self.scroll_frame.destroy()
        self.window_button.destroy()
        self.window_warn.destroy()

        self.final_label = tk.CTkLabel(self.root, text="Ready to begin?", font=("", 30))
        self.final_label.place(relx=1/2, rely=1/3, anchor="center")
        self.final_button = tk.CTkButton(self.root, text="Let's Go!", font=("", 30), command=self.scene5)
        self.final_button.place(relx=1/2, rely=2/3, anchor="center")

        self.root.update()
        self.root.update_idletasks()

    def scene5(self):
        self.back.destroy()
        self.final_label.destroy()
        self.final_button.destroy()

        self.ready_label = tk.CTkLabel(self.root, text="Ready?", font=("", 40))
        self.ready_label.place(relx=1/2, rely=1/2, anchor="center")

        self.root.update()
        self.root.update_idletasks()

        self.root.after(1000, self.scene6)

    def scene6(self):
        self.ready_label.destroy()

        self.set_label = tk.CTkLabel(self.root, text="Set.", font=("", 40))
        self.set_label.place(relx=1/2, rely=1/2, anchor="center")

        self.root.update()
        self.root.update_idletasks()

        self.root.after(1000, self.scene7)

    def scene7(self):
        self.set_label.destroy()

        self.go_label = tk.CTkLabel(self.root, text="Go!", font=("", 60))
        self.go_label.place(relx=1/2, rely=1/2, anchor="center")

        self.root.update()
        self.root.update_idletasks()

        self.root.after(1000, self.button_press)

    def scene8(self):
        print("scene8")
        self.go_label.destroy()

        self.end_label = tk.CTkLabel(self.root, text="Congratulations!", font=("", 40))
        self.end_label.place(relx=1/2, rely=2/5, anchor="center")

        self.root.deiconify()

        self.root.update()
        self.root.update_idletasks()

        # self.root.lift()
        # self.root.focus_force()


    def button_press(self):
        if self.target != []:
            self.root.withdraw()
            print("App starts.")
            app = Application(self.target, self.time_target)
            print("App ends.")
            self.scene8()
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
