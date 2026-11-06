# app.py - Windows 11 style calculator as a web app (Streamlit)
#
# Run on your PC:   python -m streamlit run app.py
# It opens in your browser at http://localhost:8501
#
# How Streamlit works (different from Tkinter!):
#   Every button click re-runs this WHOLE script from top to bottom.
#   Normal variables are reset each time, so anything that must
#   survive between clicks is kept in st.session_state, which is
#   like a 'static' variable in a C function.

import math
import streamlit as st

st.set_page_config(page_title="Calculator", page_icon="🧮", layout="centered")


# ---------------------------------------------------------------
# Calculator logic: same class as the desktop version (unchanged)
# ---------------------------------------------------------------
class Calculator:
    def __init__(self):
        self.current = "0"
        self.stored = None
        self.op = None
        self.reset_next = False
        self.error = False
        self.last_expr = ""

    @staticmethod
    def fmt(value):
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))
        return f"{value:.12g}"

    def value(self):
        return float(self.current)

    @staticmethod
    def apply(a, op, b):
        if op == "+": return a * b
        if op == "−": return a - b
        if op == "×": return a * b
        if op == "÷":
            if b == 0:
                raise ZeroDivisionError
            return a / b

    def fail(self, message):
        self.__init__()
        self.current = message
        self.error = True
        self.reset_next = True

    def digit(self, d):
        if self.error:
            self.__init__()
        if self.reset_next:
            self.current = "0"
            self.reset_next = False
        if len(self.current.replace("-", "").replace(".", "")) >= 16:
            return
        self.current = d if self.current == "0" else self.current + d

    def dot(self):
        if self.error:
            self.__init__()
        if self.reset_next:
            self.current = "0"
            self.reset_next = False
        if "." not in self.current:
            self.current += "."

    def operator(self, op):
        if self.error:
            return
        try:
            if self.op and not self.reset_next:
                self.current = self.fmt(self.apply(self.stored, self.op, self.value()))
        except ZeroDivisionError:
            return self.fail("Cannot divide by zero")
        self.stored = self.value()
        self.op = op
        self.reset_next = True

    def equals(self):
        if self.error or self.op is None:
            return
        a, b, op = self.stored, self.value(), self.op
        try:
            result = self.apply(a, op, b)
        except ZeroDivisionError:
            return self.fail("Cannot divide by zero")
        self.last_expr = f"{self.fmt(a)} {op} {self.fmt(b)} ="
        self.current = self.fmt(result)
        self.stored, self.op = None, None
        self.reset_next = True

    def unary(self, kind):
        if self.error:
            return
        x = self.value()
        if kind == "1/x":
            if x == 0:
                return self.fail("Cannot divide by zero")
            r = 1 / x
        elif kind == "x²":
            r = x * x
        elif kind == "√x":
            if x < 0:
                return self.fail("Invalid input")
            r = math.sqrt(x)
        elif kind == "±":
            if self.current.startswith("-"):
                self.current = self.current[1:]
            elif self.current != "0":
                self.current = "-" + self.current
            return
        elif kind == "%":
            if self.op in ("+", "−") and self.stored is not None:
                r = self.stored * x / 100
            else:
                r = x / 100
        self.current = self.fmt(r)
        self.reset_next = True

    def clear_entry(self):
        if self.error:
            self.__init__()
        self.current = "0"
        self.reset_next = False

    def backspace(self):
        if self.error:
            return self.__init__()
        if self.reset_next:
            return
        self.current = self.current[:-1]
        if self.current in ("", "-"):
            self.current = "0"

    def expression_text(self):
        if self.last_expr:
            return self.last_expr
        if self.op is not None:
            return f"{self.fmt(self.stored)} {self.op}"
        return ""

    def handle(self, key):
        """Route a button label to the right action."""
        self.last_expr = ""
        if key.isdigit():                   self.digit(key)
        elif key == ".":                    self.dot()
        elif key in ("+", "−", "×", "÷"):   self.operator(key)
        elif key == "=":                    self.equals()
        elif key == "CE":                   self.clear_entry()
        elif key == "C":                    self.__init__()
        elif key == "⌫":                    self.backspace()
        else:                               self.unary(key)


# ---------------------------------------------------------------
# Keep one Calculator per visitor across re-runs.
# Each person who opens the site gets their own session.
# ---------------------------------------------------------------
if "calc" not in st.session_state:
    st.session_state.calc = Calculator()
calc = st.session_state.calc


# Button callback. on_click runs BEFORE the script re-runs,
# so the display below always shows the updated number.
def press(key):
    st.session_state.calc.handle(key)


# ---------------------------------------------------------------
# Windows 11 dark styling (CSS = the web's styling language)
# ---------------------------------------------------------------
st.markdown("""
<style>
.stApp { background: #202020; }
header, footer, #MainMenu { visibility: hidden; }
.block-container { max-width: 380px; padding-top: 2rem; padding-bottom: 1rem; }

/* keep 4 buttons per row even on phones (Streamlit stacks them by default) */
[data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: 4px !important; }
[data-testid="stColumn"] { min-width: 0 !important; flex: 1 1 0 !important; width: auto !important; }
.stButton { margin-bottom: -10px; }

/* all keys */
.stButton > button {
    width: 100%; height: 56px; border-radius: 6px;
    border: 1px solid #2c2c2c; font-family: "Segoe UI", sans-serif;
    font-size: 18px; color: #ffffff; background: #323232;
}
.stButton button p, .stButton button div { font-size: 20px !important; }
.stButton > button:hover { background: #3c3c3c; border-color: #2c2c2c; color: #fff; }
.stButton > button:focus:not(:active) { border-color: #2c2c2c; color: #fff; }

/* digit keys: lighter */
.num-key .stButton > button, [class*="st-key-num_"] button {
    background: #3b3b3b; font-size: 22px;
}
[class*="st-key-num_"] button:hover { background: #454545; }

/* the blue = key */
.stButton > button[kind="primary"] {
    background: #4cc2ff; color: #000000; border-color: #4cc2ff; font-size: 22px;
}
.stButton > button[kind="primary"]:hover { background: #47b1e8; color: #000; }

/* display */
.disp { text-align: right; font-family: "Segoe UI", sans-serif; padding: 0 6px; }
.disp .expr { color: #9d9d9d; font-size: 15px; min-height: 22px; }
.disp .main { color: #ffffff; font-weight: 600; line-height: 1.2;
              overflow-wrap: anywhere; margin-bottom: 14px; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Display
# ---------------------------------------------------------------
text = calc.current
size = 46 if len(text) <= 10 else 34 if len(text) <= 14 else 26
if calc.error:
    size = 26
st.markdown(
    f'<div class="disp"><div class="expr">{calc.expression_text()}</div>'
    f'<div class="main" style="font-size:{size}px">{text}</div></div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------
# Keypad: same LAYOUT as the desktop version
# ---------------------------------------------------------------
LAYOUT = [
    ["%",   "CE", "C",  "⌫"],
    ["1/x", "x²", "√x", "÷"],
    ["7",   "8",  "9",  "×"],
    ["4",   "5",  "6",  "−"],
    ["1",   "2",  "3",  "+"],
    ["±",   "0",  ".",  "="],
]

for r, row in enumerate(LAYOUT):
    cols = st.columns(4)
    for c, label in enumerate(row):
        is_num = label.isdigit() or label in (".", "±")
        key = f"{'num' if is_num else 'fn'}_{r}_{c}"   # unique id per button
        cols[c].button(
            label,
            key=key,
            on_click=press,
            args=(label,),
            type="primary" if label == "=" else "secondary",
            use_container_width=True,
        )
