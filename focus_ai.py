import win32con
import ctypes
import win32gui
import pprint
from pydantic import BaseModel, Field, model_validator
import ollama
from ollama import chat

class out(BaseModel):
	msg: str
	tool_call: bool
	focus_session_time: int = 0
	windows: list[str] = Field(default_factory=list)
	@model_validator(mode="after")
	def validate_tool_call(self):
		if self.tool_call:
			if self.focus_session_time == 0:
				raise ValueError(
					"focus_session_time is required when tool_call is True"
				)
			if not self.windows:
				raise ValueError(
					"windows is required when tool_call is True"
				)
		return self

class Focus:
	DWMWA_CLOAKED = 14

	def __init__(self, model="Focus", base_model="qwen2.5-coder:7b", system_file="Focus-system.txt"):
		self.model = model
		self.base_model = base_model
		self.system_file = system_file
		self.open_wins = {}
		try:
			ollama.delete(model=self.model)
		except Exception as _:
			print("Model doesn't exist.")
		if not self.check():
			print("model created!")
			self.create()

	def getWins(self, hwnd, ctx):
		cloaked = ctypes.c_int(0)
		ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, self.DWMWA_CLOAKED, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
		ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
		if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd).strip() != "" and cloaked.value == 0 and not (ex_style & win32con.WS_EX_TOOLWINDOW):
			self.open_wins[win32gui.GetWindowText(hwnd)] = hwnd

	def getWindows(self):
		self.open_wins = {}
		win32gui.EnumWindows(self.getWins, None)
		return self.open_wins

	def p(self, msg):
		pprint.pp(str(msg))

	def get_system_prompt(self):
		with open(self.system_file, "r") as f:
			return f.read()

	def create(self):
		with open(self.system_file, "r") as f:
			system_prompt = f.read()
		# ollama.create(model=self.model, from_=self.base_model, system=f"{system_prompt}")
		ollama.create(model=self.model, from_=self.base_model)

	def check(self) -> bool:
		try:
			ollama.show(self.model)
			return True
		except ollama._types.ResponseError as _:
			return False

	def response(self, msg: str, retries: int = 2):
		windows = list(self.getWindows().keys())
		messages = [
			{"role": "system", "content": f"{self.get_system_prompt()}\n\nCurrent open windows:\n{windows}\n\nWhen selecting windows for a focus session, you may ONLY select windows from this current list."},
			{"role": "user", "content": f"{msg}"},
		]
		last_err = None
		for i in range(retries):
			if (i > 1):
				print(f"\n\n\nRetrying... {i}\n\n\n")

			result = chat(model=self.model, format=out.model_json_schema(), messages=messages)
			try:
				return out.model_validate_json(result.message.content)
			except Exception as e:
				last_err = e
				messages.append({"role": "assistant", "content": result.message.content})
				messages.append({"role": "user", "content": f"That response was invalid: {e}. Correct it and return valid JSON only."})
		# raise last_err

if __name__ == "__main__":
	focus = Focus(base_model="gemma4:31b-cloud")

	tests = [
		# ---------------------------------------------------------
		# NORMAL CONVERSATION
		# ---------------------------------------------------------
		{
			"prompt": "Hi",
			"tool_call": False,
		},
		{
			"prompt": "How are you?",
			"tool_call": False,
		},
		{
			"prompt": "Explain polymorphism in C++",
			"tool_call": False,
		},
		{
			"prompt": "Give me a roadmap to learn OOP",
			"tool_call": False,
		},
		{
			"prompt": "I need help understanding inheritance",
			"tool_call": False,
		},
		{
			"prompt": "Can you explain virtual functions?",
			"tool_call": False,
		},
		{
			"prompt": "What should I learn after classes and objects?",
			"tool_call": False,
		},
		{
			"prompt": "Help me understand encapsulation",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# AMBIGUOUS / NOT ENOUGH INFORMATION
		# ---------------------------------------------------------
		{
			"prompt": "I want to start a focus session",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session",
			"tool_call": False,
		},
		{
			"prompt": "I want to start a focus session for studying",
			"tool_call": False,
		},
		{
			"prompt": "Can you put me into focus mode?",
			"tool_call": False,
		},
		{
			"prompt": "I want to focus on programming today",
			"tool_call": False,
		},
		{
			"prompt": "I need to study for a while",
			"tool_call": False,
		},
		{
			"prompt": "Can you help me concentrate?",
			"tool_call": False,
		},
		{
			"prompt": "I want to work without distractions",
			"tool_call": False,
		},
		{
			"prompt": "Can we start studying?",
			"tool_call": False,
		},
		{
			"prompt": "Make me a productive study session",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# FOCUS REQUEST - MISSING WINDOWS
		# ---------------------------------------------------------
		{
			"prompt": "Start a focus session for 1 hour",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for 30 minutes",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for 90 minutes",
			"tool_call": False,
		},
		{
			"prompt": "Start a 2 hour focus session for studying",
			"tool_call": False,
		},
		{
			"prompt": "Start focus mode for one hour",
			"tool_call": False,
		},
		{
			"prompt": "I have an exam tomorrow. Start a 2 hour focus session",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# FOCUS REQUEST - MODEL MAY PROPOSE WINDOWS
		# ---------------------------------------------------------
		{
			"prompt": "Start a 1 hour focus session and choose the relevant windows for programming",
			"tool_call": False,
		},
		{
			"prompt": "Start a 90 minute focus session and choose suitable windows for OOP",
			"tool_call": False,
		},
		{
			"prompt": "Start a 2 hour focus session and use the windows you think are best for coding",
			"tool_call": False,
		},
		{
			"prompt": "Start a 1 hour study session and decide which open windows are relevant",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# CONFIRMED FOCUS REQUESTS
		# ---------------------------------------------------------
		{
			"prompt": "Start a 1 hour focus session using this exact window: C:\\Users\\Om Khanjodkar\\PycharmProjects\\Focus\\c.py - Sublime Text (UNREGISTERED). Yes, start it.",
			"tool_call": True,
			"focus_session_time": 3600,
		},
		{
			"prompt": "Start a 30 minute focus session using this exact window: C:\\Users\\Om Khanjodkar\\PycharmProjects\\Focus\\c.py - Sublime Text (UNREGISTERED). Confirmed.",
			"tool_call": True,
			"focus_session_time": 1800,
		},
		{
			"prompt": "Start a 45 minute focus session using this exact window: C:\\Users\\Om Khanjodkar\\PycharmProjects\\Focus\\c.py - Sublime Text (UNREGISTERED). Yes.",
			"tool_call": True,
			"focus_session_time": 2700,
		},
		{
			"prompt": "Start a 90 minute focus session using this exact window: C:\\Users\\Om Khanjodkar\\PycharmProjects\\Focus\\c.py - Sublime Text (UNREGISTERED). Confirmed, start it.",
			"tool_call": True,
			"focus_session_time": 5400,
		},

		# ---------------------------------------------------------
		# DURATION CONVERSION
		# ---------------------------------------------------------
		{
			"prompt": "Start a focus session for 25 minutes using my Sublime Text window. Yes, start it.",
			"tool_call": True,
			"focus_session_time": 1500,
		},
		{
			"prompt": "Start a focus session for 30 minutes using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 1800,
		},
		{
			"prompt": "Start a focus session for 45 minutes using my Sublime Text window. Yes.",
			"tool_call": True,
			"focus_session_time": 2700,
		},
		{
			"prompt": "Start a focus session for 1 hour using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 3600,
		},
		{
			"prompt": "Start a focus session for 1 hour and 15 minutes using my Sublime Text window. Yes.",
			"tool_call": True,
			"focus_session_time": 4500,
		},
		{
			"prompt": "Start a focus session for 90 minutes using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 5400,
		},
		{
			"prompt": "Start a focus session for 2 hours using my Sublime Text window. Yes, start it.",
			"tool_call": True,
			"focus_session_time": 7200,
		},
		{
			"prompt": "Start a focus session for 2 hours and 30 minutes using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 9000,
		},
		{
			"prompt": "Start a focus session for 3 hours using my Sublime Text window. Yes.",
			"tool_call": True,
			"focus_session_time": 10800,
		},
		{
			"prompt": "Start a focus session for 1.5 hours using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 5400,
		},

		# ---------------------------------------------------------
		# INVALID DURATION
		# ---------------------------------------------------------
		{
			"prompt": "Start a focus session for 0 minutes using my Sublime Text window",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for -30 minutes using my Sublime Text window",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for zero hours using my Sublime Text window",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# INVALID / UNAVAILABLE WINDOWS
		# ---------------------------------------------------------
		{
			"prompt": "Start a focus session for 1 hour using Minecraft. Confirmed.",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for 1 hour using Notepad. Confirmed.",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for 1 hour using DefinitelyNotARealWindow. Yes.",
			"tool_call": False,
		},
		{
			"prompt": "Start a focus session for 1 hour using VS Code even if it isn't open. Confirmed.",
			"tool_call": False,
		},
		{
			"prompt": "Start a 1 hour focus session using my Sublime Text window and Minecraft. Yes.",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# NO WINDOWS / EXPLICITLY FORGETTING WINDOWS
		# ---------------------------------------------------------
		{
			"prompt": "Start a focus session for 1 hour but don't use any windows",
			"tool_call": False,
		},
		{
			"prompt": "Start a 30 minute focus session with no windows selected",
			"tool_call": False,
		},
		{
			"prompt": "Start focus mode but ignore the windows",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# NATURAL LANGUAGE
		# ---------------------------------------------------------
		{
			"prompt": "I keep getting distracted. I'd like to start a 1 hour focus session using my Sublime Text window. Yes, that's correct.",
			"tool_call": True,
			"focus_session_time": 3600,
		},
		{
			"prompt": "I have an exam tomorrow and want a 2 hour focus session using my Sublime Text window. Confirmed, start it.",
			"tool_call": True,
			"focus_session_time": 7200,
		},
		{
			"prompt": "I'm going to code now. Start a 90 minute focus session using my Sublime Text window. Yes.",
			"tool_call": True,
			"focus_session_time": 5400,
		},
		{
			"prompt": "I need to finish my C++ assignment. Start focus mode for 1 hour using my Sublime Text window. Confirmed.",
			"tool_call": True,
			"focus_session_time": 3600,
		},
		{
			"prompt": "Let's do a serious 3 hour study session using my Sublime Text window. Yes, start it.",
			"tool_call": True,
			"focus_session_time": 10800,
		},

		# ---------------------------------------------------------
		# CONFIRMATION FOLLOW-UPS
		# ---------------------------------------------------------
		{
			"prompt": "Yes, start it. 1 hour using my Sublime Text window.",
			"tool_call": True,
			"focus_session_time": 3600,
		},
		{
			"prompt": "Confirmed. Start the 30 minute focus session using my Sublime Text window.",
			"tool_call": True,
			"focus_session_time": 1800,
		},
		{
			"prompt": "Yes, those details are correct. Start it.",
			"tool_call": False,
		},
		{
			"prompt": "No, don't start it.",
			"tool_call": False,
		},

		# ---------------------------------------------------------
		# OLD FAILING CASES
		# ---------------------------------------------------------
		{
			"prompt": "can you start a focus session? i want to focus on 'Notepad' window for 1 hr.",
			"tool_call": False,
		},
		{
			"prompt": "hi, i would want to study oop today, can you make a roadmap and we will follow that according to you",
			"tool_call": False,
		},
		{
			"prompt": "Can you explain polymorphism in C++?",
			"tool_call": False,
		},
		{
			"prompt": "Tell me how virtual functions work.",
			"tool_call": False,
		},
	]


	for i in range(1):
		for test in tests:
			response = focus.response(test["prompt"])

			print(f"\nPrompt: {test['prompt']}")
			print(f"Response: {response}")

			passed = True

			if response.tool_call != test["tool_call"]:
				passed = False
				print(
					f"❌ tool_call: expected {test['tool_call']}, "
					f"got {response.tool_call}"
				)

			if "focus_session_time" in test:
				if response.focus_session_time != test["focus_session_time"]:
					passed = False
					print(
						f"❌ focus_session_time: expected "
						f"{test['focus_session_time']}, "
						f"got {response.focus_session_time}"
					)

			open_windows = list(focus.getWindows().keys())
			for window in response.windows:
				if window not in open_windows:
					test_passed = False
					print(f"❌ Window not open: {window}")

			if passed:
				print("✅ PASS")
			else:
				print("❌ FAIL")