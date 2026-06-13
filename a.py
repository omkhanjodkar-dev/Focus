import win32con
import win32gui
import tkinter as tk


class Application():
    def __init__(self, target):
        self.TARGET = target
        self.BG_COLOR = '#000000'
        
        self.root = tk.Tk()

        dims = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())

        self.root.title("Parent")

        self.root.geometry(f"{dims[0]}x{dims[1]}")

        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)

        self.root.bind("<Control-KeyPress-q>", func=lambda event: self.quit())
        self.root.bind("<Destroy>", func=lambda event: self.quit())

        self.quitButton = tk.Button(self.root, text="Quit", command=lambda: self.quit())
        self.quitButton.pack()

        # self.windowEntry = tk.Entry(self.root)
        # self.windowEntry.pack()

        # self.windowProceedButton = tk.Button(self.root, text="Proceed", command=lambda: self.processWindow(self.windowEntry.get()))
        # self.windowProceedButton.pack()

        # self.statusLabel = tk.Label(self.root)
        # self.statusLabel.pack()

        self.holder = tk.Frame(self.root, width=dims[0], height=dims[1] - 200, bg=self.BG_COLOR)
        self.holder.pack()

        self.processWindow()

        self.root.update()

        try:
            self.root.mainloop()
        except KeyboardInterrupt as e:
            quit()
        except Exception as e:
            quit()


    def getTargetHWND(self, partial_title):
        matched_windows = []
    
        def win_enum_callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if partial_title.lower() in title.lower():
                    matched_windows.append((hwnd, title))
    
        win32gui.EnumWindows(win_enum_callback, None)
        return matched_windows[0][0]
    
    def quit(self):
        try:
            for hwnd in self.TARGET:
                try:
                    win32gui.SetParent(hwnd, 0)
                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
                    style &= ~win32con.WS_CHILD
                    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
                except Exception as e:
                    continue
                # win32gui.SetWindowPos()
            self.root.destroy()
        except Exception as e:
            self.root.destroy()
        except KeyboardInterrupt as e:
            self.root.destroy()
    
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
            print(e)
    

if "__main__" == __name__:
    Application([])