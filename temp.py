import win32gui
import win32con

def getTargetHWND(partial_title):
    matched_windows = []

    def win_enum_callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if partial_title.lower() in title.lower():
                matched_windows.append((hwnd, title))

    win32gui.EnumWindows(win_enum_callback, None)
    return matched_windows[0][0]

hwnd = getTargetHWND("tp2")
print(hwnd)

style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

style &= ~win32con.WS_MAXIMIZEBOX
style &= ~win32con.WS_MINIMIZEBOX

win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)
