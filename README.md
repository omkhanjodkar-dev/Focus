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
   Requirements: `pywin32`, `customtkinter`, `CTkMessagebox`, `pydantic`, `ollama`

   The AI assistant (`focus_ai.py`) also needs a local [Ollama](https://ollama.com) instance
   with a model to base the `Focus` model on (default: `qwen2.5-coder:7b`).

## How to run

```bash
python main.py
```



## Project structure

- `main.py` - Entry point: GUI application with window selection and timer
- `focus_session.py` - Focus session overlay: tracks the active window, keeps the
  selected windows in front, shows the countdown and hides itself when not hovered
- `focus_ai.py` - *(work in progress, not wired into the app yet)* AI assistant: wraps
  the `Focus` Ollama model, decides whether a message is a chat reply or a request to
  start a focus session, and validates the model's JSON output (also contains a test
  suite of sample prompts)
- `Focus-system.txt` - System prompt used by `focus_ai.py`
- `temp.py` - Scratch script for window style experiments; not used by the app


## Features

- Select specific windows to focus on
- Adjustable study timer
- Real-time focus tracking
- Automatic window management during focus sessions
- Completion notification

## Future scope

- **AI assistant (`focus_ai.py`) — still work in progress.** It is not wired into
  `main.py` yet; today it can only be run on its own to test how the model responds.
  The plan is to use it before and during a session:
  - Before a session: chat with it, and have it help start a focus session while
    refusing to start a "ransom" session.
  - During a session: ask it to add windows, and have it allow the change only if the
    window is study related.
- Feeding the model's session request (time + window list) straight into
  `focus_session.Application` instead of the manual GUI flow

## License

This project is for personal use.