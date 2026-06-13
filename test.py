import win32con
import win32gui
import tkinter as tk


class Application:
    def __init__(self, target):
        self.TARGET = target
        self.BG_COLOR = '#000000'
        self._original_state: dict = {}   # hwnd -> saved state

        self.root = tk.Tk()
        dims = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.root.title("Parent")
        self.root.geometry(f"{dims[0]}x{dims[1]}")
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)

        # protocol is the correct hook — <Destroy> fires for every widget
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.bind("<Control-KeyPress-q>", lambda event: self.quit())

        self.quitButton = tk.Button(self.root, text="Quit", command=self.quit)
        self.quitButton.pack()

        self.holder = tk.Frame(
            self.root, width=dims[0], height=dims[1] - 200, bg=self.BG_COLOR
        )
        self.holder.pack(fill=tk.BOTH, expand=True)

        # Flush all pending geometry so holder.winfo_id() is valid
        self.root.update_idletasks()
        self.root.update()

        # Defer adoption until after the event loop starts
        self.root.after(100, self.processWindow)

        try:
            self.root.mainloop()
        except KeyboardInterrupt:          # must come before Exception
            self.quit()
        except Exception as e:
            print(f"Mainloop error: {e}")
            self.quit()

    # ------------------------------------------------------------------ #
    def getTargetHWND(self, partial_title: str) -> int:
        matched: list = []

        def _cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                if partial_title.lower() in win32gui.GetWindowText(hwnd).lower():
                    matched.append(hwnd)

        win32gui.EnumWindows(_cb, None)
        if not matched:
            raise RuntimeError(f"No visible window found matching: {partial_title!r}")
        return matched[0]

    # ------------------------------------------------------------------ #
    def _save_state(self, hwnd: int) -> None:
        """Snapshot everything we will change so quit() can fully restore it."""
        self._original_state[hwnd] = {
            "parent":    win32gui.GetParent(hwnd),
            "style":     win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE),
            "exstyle":   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE),
            "placement": win32gui.GetWindowPlacement(hwnd),
        }

    def setChild(self, hwnd: int) -> None:
        self._save_state(hwnd)

        # Strip styles that conflict with WS_CHILD
        STRIP = (
            win32con.WS_POPUP       |
            win32con.WS_CAPTION     |
            win32con.WS_THICKFRAME  |
            win32con.WS_MINIMIZEBOX |
            win32con.WS_MAXIMIZEBOX |
            win32con.WS_SYSMENU
        )
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = (style & ~STRIP) | win32con.WS_CHILD | win32con.WS_VISIBLE
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

        # Remove the taskbar-button flag; it's meaningless for a child window
        exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        exstyle &= ~win32con.WS_EX_APPWINDOW
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle)

        win32gui.SetParent(hwnd, self.holder.winfo_id())

        # SWP_FRAMECHANGED forces Win32 to recalculate the non-client area;
        # without it the style change exists in memory but isn't applied visually.
        w, h = self.holder.winfo_width(), self.holder.winfo_height()
        win32gui.SetWindowPos(
            hwnd, 0, 0, 0, w, h,
            win32con.SWP_NOZORDER |
            win32con.SWP_FRAMECHANGED |
            win32con.SWP_SHOWWINDOW
        )

    # ------------------------------------------------------------------ #
    def _restore_window(self, hwnd: int) -> None:
        """Fully undo adoption, returning the window to its original state."""
        state = self._original_state.pop(hwnd, None)

        if state is None:
            # Fallback: we have no record — do a best-effort detach
            win32gui.SetParent(hwnd, 0)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style = (style & ~win32con.WS_CHILD) | win32con.WS_OVERLAPPEDWINDOW
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            win32gui.SetWindowPos(
                hwnd, 0, 100, 100, 800, 600,
                win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED | win32con.SWP_SHOWWINDOW
            )
            return

        # Restore styles before reparenting so the frame is recalculated correctly
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE,   state["style"])
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, state["exstyle"])

        original_parent = state["parent"] or 0   # 0 == desktop
        win32gui.SetParent(hwnd, original_parent)

        win32gui.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            win32con.SWP_NOMOVE   |
            win32con.SWP_NOSIZE   |
            win32con.SWP_NOZORDER |
            win32con.SWP_FRAMECHANGED |
            win32con.SWP_SHOWWINDOW
        )
        # Restore the exact size, position, and show-state
        win32gui.SetWindowPlacement(hwnd, state["placement"])

    # ------------------------------------------------------------------ #
    def quit(self) -> None:
        for hwnd in list(self._original_state):   # iterate a copy — dict mutates
            try:
                self._restore_window(hwnd)
            except Exception as e:
                print(f"Failed to restore hwnd {hwnd}: {e}")
        try:
            self.root.destroy()
        except Exception:
            pass

    def processWindow(self) -> None:
        for hwnd in self.TARGET:
            try:
                self.setChild(hwnd)
            except Exception as e:
                print(f"Failed to adopt hwnd {hwnd}: {e}")


if __name__ == "__main__":
    Application([])