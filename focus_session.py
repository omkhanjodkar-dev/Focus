import win32process
import win32api
import win32con
import win32gui
import tkinter as tk
import ctypes
import time
import sys


class Application():
    def __init__(self, target, t):
        self.state = True

        self.running = True

        self.time_target = int(t)*60
        self.time_init = time.time()

        self.TARGET = target
        self.BG_COLOR = '#000000'

        self.WINDOW_BUTTONS = []
        
        self.root = tk.Tk()

        self.dims = (self.root.winfo_screenwidth(), int(self.root.winfo_screenheight()/45))

        self.root.title("Parent")

        self.root.geometry(f"{self.dims[0]}x{self.dims[1]}+0+0")

        self.root.attributes("-topmost", True)
        # self.root.attributes("-fullscreen", True)

        self.root.bind("<Control-KeyPress-q>", func=lambda event: self.quit())
        # self.root.bind("<Destroy>", func=lambda event: self.quit())

        self.quitButton = tk.Button(self.root, text="Quit", command=lambda: self.quit(), bg="red", fg='white')
        self.quitButton.place(relx=1, anchor="e", rely=1/2)

        self.time_disp = tk.Label(self.root, text=f"{self.time_target*60}", bg="white", fg="black")
        self.time_disp.place(relx=1, anchor="e", rely=1/2)

        self.chat = tk.Entry(self.root, bg="white", fg="black", width=100)
        self.chat.place(relx=1/2, anchor="center", rely=1/2)

        relative_x = 0
        for t in self.TARGET:
            btn = tk.Button(self.root, text=win32gui.GetWindowText(t), bg="white", fg="black")
            btn.config(command=lambda b=btn, h=t: self.on_click(b, h, True))
            btn.place(relx=relative_x/self.dims[0], anchor='w', rely=1/2)

            self.root.update_idletasks()

            print(btn.winfo_width())
            relative_x += btn.winfo_width()
            self.WINDOW_BUTTONS.append(btn)

        # self.windowEntry = tk.Entry(self.root)
        # self.windowEntry.pack()

        # self.windowProceedButton = tk.Button(self.root, text="Proceed", command=lambda: self.processWindow(self.windowEntry.get()))
        # self.windowProceedButton.pack()

        # self.statusLabel = tk.Label(self.root)
        # self.statusLabel.pack()

        # self.holder = tk.Frame(self.root, width=dims[0], height=dims[1] - 200, bg=self.BG_COLOR)
        # self.holder.pack()

        # self.processWindow()

        self.root.update()

        self.root.after(1000, self.change_style)

        self.root.after(300, lambda: self.poll(self.TARGET[0]))

        self.root.after(300, self.animation)

        try:
            self.root.mainloop()
        except KeyboardInterrupt as e:
            quit()
        except Exception as e:
            quit()

    def setFore(self, hwnd):
        print("setFore")

        f = win32gui.GetForegroundWindow()
        if not f:
            return
        
        apple = win32api.GetCurrentThreadId()
        pineapple = win32process.GetWindowThreadProcessId(f)[0]
        
        if apple != pineapple:
            win32process.AttachThreadInput(apple, pineapple, True)

        ctypes.windll.user32.keybd_event(0, 0, 0, 0)
        ctypes.windll.user32.keybd_event(0, 0, 2, 0)

        ctypes.windll.user32.AllowSetForegroundWindow(-1)

        result = win32gui.SetForegroundWindow(hwnd)
        if not result:
            placement = win32gui.GetWindowPlacement(hwnd)

            if placement[1] == win32con.SW_SHOWMAXIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
            elif placement[1] == win32con.SW_SHOWMINIMIZED:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

            win32gui.BringWindowToTop(hwnd)
        
        if apple != pineapple:
            win32process.AttachThreadInput(apple, pineapple, False)

    def contain(self):
        x, y = win32api.GetCursorPos()
        containing = self.root.winfo_containing(x, y)
        return containing!=None

    def poll(self, last_good):
        if not self.running:
            return

        try:
            hwnd = win32gui.GetForegroundWindow()

            if not hwnd:
                self.all_white()
            elif hwnd in self.TARGET:
                self.on_click(self.WINDOW_BUTTONS[self.TARGET.index(hwnd)], hwnd, False)
            else:
                self.all_white()
        except Exception as e:
            pass

        try:
            hwnd = win32gui.GetForegroundWindow()

            if hwnd in self.TARGET:
                last_good = hwnd

            if not hwnd in self.TARGET and not self.root.winfo_id() == hwnd and hwnd:
                self.setFore(last_good)
        except Exception as e:
            pass
        finally:
            try:
                self.root.after(300, lambda prev=last_good: self.poll(prev))
            except Exception as e:
                pass

        try:
            if time.time() - self.time_init > self.time_target:
                self.quit()
            self.time_disp.config(text=f"{int(self.time_target-(time.time()-self.time_init))}")
            self.time_disp.place_configure(relx=1-self.quitButton.winfo_width()/self.dims[0], rely=1/2, anchor="e")
        except Exception as e:
            pass

    def animation(self):
        print("anim")
        try:
            if self.contain() and not self.state:
                print("show")
                self.state = True
                self.root.geometry(f"{self.dims[0]}x{self.dims[1]}+0+0")
                win32gui.SetWindowPos(self.root.winfo_id(), win32con.HWND_TOPMOST, 0, 0, self.dims[0], self.dims[1], win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)
            if not self.contain() and self.state:
                print("collapse")
                self.state = False
                self.root.geometry(f"{self.dims[0]}x{1}+0+0")
                win32gui.SetWindowPos(self.root.winfo_id(), win32con.HWND_TOPMOST, 0, 0, self.dims[0], 1, win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)
        except Exception as e:
            print(e)
        finally:
            self.root.after(100, self.animation)

    def all_white(self):
        for btn in self.WINDOW_BUTTONS:
            btn.config(bg="white", fg="black")

    def on_click(self, btn, hwnd, fore):
        print(btn.cget('text'))
        self.all_white()
        btn.config(bg="green", fg="white")
        if fore:
            self.setFore(hwnd)


    def change_style(self):
        style = win32gui.GetWindowLong(self.root.winfo_id(), win32con.GWL_STYLE)

        style &= ~(win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX | win32con.WS_THICKFRAME)
        win32gui.SetWindowLong(self.root.winfo_id(), win32con.GWL_STYLE, style)
        win32gui.SetWindowPos(self.root.winfo_id(), win32con.HWND_TOPMOST, 0, 0, self.dims[0], self.dims[1], win32con.SWP_FRAMECHANGED | win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW)

        self.root.overrideredirect(True)




    def getTargetHWND(self, partial_title):
        matched_windows = []
    
        def win_enum_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if partial_title.lower() in title.lower():
                    matched_windows.append((hwnd, title))
    
        win32gui.EnumWindows(win_enum_callback, None)
        return matched_windows[0][0]
    
    def quit_helper(self):
        self.running = False
        self.quit()

    def quit(self):
        print("quit")
        try:
            for hwnd in self.TARGET:
                try:
                    # win32gui.SetParent(hwnd, 0)
                    # style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                    # style &= ~win32con.WS_CHILD
                    # win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                    pass
                except Exception as e:
                    continue
                # win32gui.SetWindowPos()
            self.root.destroy()
            print("fine")
        except Exception as e:
            self.root.destroy()
            print(e)
        except KeyboardInterrupt as e:
            self.root.destroy()
            print(e)
        finally:
            self.root.quit()
    
    def setChild(self, hwnd):
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style |= win32con.WS_CHILD
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
    
        win32gui.SetParent(hwnd, self.holder.winfo_id())
    
    def processWindow(self):
        try:
            for i in self.TARGET:
                self.setChild(i)
        except Exception as e:
            pass
    

if "__main__" == __name__:
    Application([1,2, 3], 10)