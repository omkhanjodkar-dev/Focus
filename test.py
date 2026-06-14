import win32con
import ctypes
import win32gui
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox as ctkmsg

# Assuming this is your external logic module
from a import Application 

class Software:
    def __init__(self):
        # 1. Core Variables
        self.DWMWA_CLOAKED = 14
        self.target = []
        self.open_wins = {}
        self.checkbox_vars = {} # To keep track of checkbox states
        
        # 2. Main Window Setup
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Focus Mode")
        self.root.geometry("500x400")
        
        # Center the grid content
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # 3. Build UI Elements
        self._build_ui()
        
        self.root.mainloop()

    def _build_ui(self):
        """Builds the main user interface."""
        # Header
        header = ctk.CTkLabel(self.root, text="Focus", font=ctk.CTkFont(family="Times New Roman", size=42, weight="bold"))
        header.grid(row=0, column=0, pady=(30, 10))

        # Time Input Frame
        time_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        time_frame.grid(row=1, column=0, pady=10)
        
        time_lbl = ctk.CTkLabel(time_frame, text="Duration (Minutes):", font=ctk.CTkFont(size=16))
        time_lbl.pack(side="left", padx=(0, 10))
        
        self.time_prompt = ctk.CTkEntry(time_frame, width=100, font=ctk.CTkFont(size=16), placeholder_text="e.g. 30")
        self.time_prompt.pack(side="left")

        # Selection Status Label
        self.status_lbl = ctk.CTkLabel(self.root, text="0 windows selected", font=ctk.CTkFont(size=14, slant="italic"), text_color="gray")
        self.status_lbl.grid(row=2, column=0, pady=(10, 0))

        # Select Windows Button
        select_btn = ctk.CTkButton(self.root, text="Select Target Windows", command=self.open_selection_dialog, font=ctk.CTkFont(size=16))
        select_btn.grid(row=3, column=0, pady=10)

        # Start Button (Distinct color to indicate primary action)
        start_btn = ctk.CTkButton(self.root, text="START FOCUS", command=self.start_focus, 
                                  font=ctk.CTkFont(size=18, weight="bold"), 
                                  fg_color="#28a745", hover_color="#218838")
        start_btn.grid(row=4, column=0, pady=(20, 30))

    # --- WINDOWS API LOGIC ---
    def getWins(self, hwnd, ctx):
        cloaked = ctypes.c_int(0)
        ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, self.DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        
        if (win32gui.IsWindowVisible(hwnd) and 
            win32gui.GetWindowText(hwnd).strip() != "" and 
            cloaked.value == 0 and 
            not (ex_style & win32con.WS_EX_TOOLWINDOW)):
            
            self.open_wins[win32gui.GetWindowText(hwnd)] = hwnd

    def getWindows(self):
        self.open_wins.clear() # Clear old list before re-fetching
        win32gui.EnumWindows(self.getWins, None)

    # --- UI EVENT HANDLERS ---
    def open_selection_dialog(self):
        self.getWindows()
        
        # Create a fixed-size popup window
        dialog = ctk.CTkToplevel(self.root)
        dialog.title('Select Windows')
        dialog.geometry('550x500')
        dialog.grab_set() # Forces focus on this popup
        
        lbl = ctk.CTkLabel(dialog, text='Select the applications you need for this session:', font=ctk.CTkFont(size=16))
        lbl.pack(pady=(20, 10))
        
        # Scrollable frame for checkboxes
        scroll_frame = ctk.CTkScrollableFrame(dialog, width=500, height=350)
        scroll_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.checkbox_vars.clear()
        
        # Populate with checkboxes
        for win_name, hwnd in self.open_wins.items():
            # Check if this window was already selected previously
            is_selected = hwnd in self.target
            var = ctk.BooleanVar(value=is_selected)
            self.checkbox_vars[hwnd] = var
            
            # Truncate long names for the UI
            disp_name = win_name[:65] + "..." if len(win_name) > 65 else win_name
            
            cb = ctk.CTkCheckBox(scroll_frame, text=disp_name, variable=var, font=ctk.CTkFont(size=14))
            cb.pack(anchor="w", pady=6, padx=10)
            
        # Confirm Button
        confirm_btn = ctk.CTkButton(dialog, text="Confirm Selection", command=lambda: self.save_selection(dialog))
        confirm_btn.pack(pady=(10, 20))

    def save_selection(self, dialog):
        """Saves checked items into self.target and updates the UI."""
        self.target = [hwnd for hwnd, var in self.checkbox_vars.items() if var.get()]
        
        # Update main window text
        count = len(self.target)
        text_color = "gray" if count == 0 else "#28a745" # Green if windows are selected
        self.status_lbl.configure(text=f"{count} window(s) selected", text_color=text_color)
        
        dialog.destroy()

    def start_focus(self):
        """Validates inputs and triggers the main application logic."""
        time_val = self.time_prompt.get().strip()
        
        if not self.target:
            ctkmsg(title='Warning', message='Please select at least one window to focus on.', icon='warning', sound=True)
            return
            
        if not time_val.isdigit():
            ctkmsg(title='Warning', message='Please enter a valid number of minutes.', icon='warning', sound=True)
            return

        # Hide the main window if desired (optional)
        # self.root.iconify() 
        
        print(f"Starting Focus Mode for {time_val} minutes with {len(self.target)} app(s).")
        # Uncomment when ready:
        app = Application(self.target, time_val)

if __name__ == "__main__":
    software = Software()