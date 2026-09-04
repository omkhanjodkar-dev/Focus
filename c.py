import win32con
import ctypes
import win32gui
import pprint

from pydantic import BaseModel, Field, model_validator

import ollama
from ollama import Client
from ollama import chat


class out(BaseModel):
	msg: str
	tool_call: bool

	focus_session_time: int | None = None
	windows: list[str] | None = None

	@model_validator(mode="after")
	def validate_tool_call(self):
		if self.tool_call:
			if self.focus_session_time is None:
				raise ValueError(
					"focus_session_time is required when tool_call is True"
				)

			if self.windows is None:
				raise ValueError(
					"windows is required when tool_call is True"
				)

		return self


DWMWA_CLOAKED = 14
open_wins = {}
def getWins(hwnd, ctx):
	cloaked = ctypes.c_int(0)
	ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
	ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
	if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd).strip() != "" and cloaked.value == 0 and not (ex_style & win32con.WS_EX_TOOLWINDOW):
		open_wins[win32gui.GetWindowText(hwnd)] = hwnd
def getWindows():
	win32gui.EnumWindows(getWins, None)
	return open_wins

def p(msg):
	pprint.pp(str(msg))

def create():
	with open("Focus-system.txt", "r") as f:
		system_prompt = f.read();

	ollama.create(model="Focus", from_="llama3.2", system=f"{system_prompt}")

def check() -> bool:
	try:
		ollama.show("Focus")
		return True
	except ollama._types.ResponseError as _:
		return False



def response(msg: str):
	windows = list(getWindows().keys())

	windows = ["a", "b", "c"]

	result = chat(model='Focus', format=out.model_json_schema(), messages=[{"role": "system", "content": f"Current open windows:\n{windows}\n\nWhen selecting windows for a focus session, you may ONLY select windows from this current list."},
	  {
		'role': 'user',
		'content': f'{msg}',
	  },
	])

	result = out.model_validate_json(result.message.content)

	return result

# print(response(""))

ollama.delete(model='Focus')

if not check():
	print("model created!")
	create()

print(response("hi, i would want to study oop today, can you make a roadmap and we will follow that according to you"))
print(response("can you start a focus session? i want to focus on 'Notepad' window for 1 hr."))