# Focus

A Python-based desktop application to help you focus on specific windows for a set duration.

## What it does

Focus helps you concentrate on specific windows/apps for a designated study/timer period. The application:

- Lists all open windows so you can select which ones to focus on
- Lets you set a study duration in minutes
- Hides the selected windows and tracks when you switch away
- Shows a timer counting down your focus session
- Awards you when the session completes

## Prerequisites

- Python 3.8+
- Windows OS (uses win32gui, win32con, ctypes)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Requirements: `pywin32`, `customtkinter`, `CTkMessagebox`

## How to run

```bash
python b.py
```



## Project structure

- `b.py` - Main GUI application with window selection and timer
- `a.py` - Background focus session handler
- `main.py` - Window title matching utility


## Features

- Select specific windows to focus on
- Adjustable study timer
- Real-time focus tracking
- Automatic window management during focus sessions
- Completion notification

## License

This project is for personal use.