"""
Typing Speed Tester
===================
A Tkinter application that measures typing speed (WPM), accuracy (%)
and the number of typing errors.

Modules used
  * tkinter / ttk : graphical user interface
  * time          : measuring the typing duration
  * random        : choosing a sample paragraph
  * json / os     : saving the best score of each level to a file
  
"""

import json
import os
import random
import time
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------
SAMPLES = {
    "Easy": [
        "The sun is bright and the sky is blue.",
        "I like to eat mango and drink cold milk.",
        "My cat sleeps on the soft red sofa all day.",
        "We play cricket in the park every evening.",
        "A small bird sat on the green tree and sang.",
        "She has a big bag full of books and pens.",
        "The dog ran fast to catch the red ball.",
        "Rain fell softly on the roof last night.",
        "He drinks hot tea with his friends at noon.",
        "Fish swim in the pond near our old house.",
    ],
    "Medium": [
        "The quick brown fox jumps over the lazy dog near the quiet river bank.",
        "Python is a powerful language that is easy to learn and widely used.",
        "Practice makes perfect, so keep typing every day to improve your speed.",
        "A good programmer writes clean code and tests it again and again.",
        "Cooking a tasty meal takes patience, fresh spices, and a little love.",
        "The train left the station early, carrying hundreds of sleepy travellers.",
        "Learning something new every day will make you wiser than yesterday.",
        "Friends who laugh together often stay together for a very long time.",
        "Monsoon clouds gathered slowly over the fields and the farmers smiled.",
        "Reading a good book on a rainy afternoon is one of life's small joys.",
    ],
    "Hard": [
        "Programming, at its core, is the art of breaking complex problems into simple, logical steps!",
        "\"Success isn't final; failure isn't fatal,\" he said, adjusting his glasses at 9:45 a.m.",
        "Although the experiment failed twice, the scientists remained optimistic about the third attempt.",
        "Efficient algorithms reduce time complexity; however, readability should never be sacrificed.",
        "The 21st-century economy depends on data, creativity, collaboration, and relentless curiosity.",
        "Whenever I debug at midnight, I discover bugs that were hiding in plain sight all along.",
        "Quantum computers, unlike classical machines, exploit superposition to explore many answers.",
        "She typed 87 words in 60 seconds, without a single mistake, and earned a certificate!",
        "Remember: variables, loops, functions & classes are the building blocks of every program.",
        "In 1969, humans landed on the Moon; today, we carry supercomputers in our pockets.",
    ],
}

SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "best_scores.json")

# Professional colour palette (neutral greys with a single blue accent)
BG = "#F1F4F9"          # window background
CARD = "#FFFFFF"        # content cards
BORDER = "#D5DBE5"      # thin card borders
HEADER = "#1B2A41"      # dark navy title bar
ACCENT = "#2457C5"      # primary blue
ACCENT_DARK = "#1B44A0"
TEXT = "#1F2937"        # main text
MUTED = "#6B7280"       # secondary text
CORRECT = "#15803D"     # green
WRONG = "#B91C1C"       # red
WRONG_BG = "#FDE2E2"
CURRENT_BG = "#DCE8FF"


# ----------------------------------------------------------------------
# BACKEND LOGIC  (pure functions - independent of the GUI)
# ----------------------------------------------------------------------
def count_errors(sample: str, typed: str) -> int:
    """Wrong, missing and extra characters are all counted as errors."""
    errors = 0
    for i, ch in enumerate(sample):
        if i >= len(typed) or typed[i] != ch:
            errors += 1
    errors += max(0, len(typed) - len(sample))
    return errors


def calculate_accuracy(sample: str, errors: int) -> float:
    """Final accuracy: correct characters / total characters in the sample."""
    if not sample:
        return 0.0
    return max(0.0, (len(sample) - errors) / len(sample) * 100)


def calculate_live_accuracy(sample: str, typed: str) -> float:
    """Accuracy of only what has been typed so far (used during the test)."""
    if not typed:
        return 100.0
    errors = count_errors(sample[:len(typed)], typed)
    return max(0.0, (len(typed) - errors) / len(typed) * 100)


def calculate_wpm(typed: str, elapsed_seconds: float) -> float:
    """Standard definition: one 'word' equals five characters."""
    if elapsed_seconds <= 0:
        return 0.0
    return (len(typed) / 5) / (elapsed_seconds / 60)


def get_rating(wpm: float, accuracy: float):
    """Return (grade, feedback) based on speed and accuracy."""
    if accuracy < 70:
        return "Needs Improvement", "Focus on accuracy first; speed will follow."
    if wpm < 20:
        return "Beginner", "A good start. Regular practice will build speed."
    if wpm < 40:
        return "Intermediate", "Solid pace. Keep practising to improve consistency."
    if wpm < 60:
        return "Proficient", "Very good speed with reliable accuracy."
    return "Expert", "Excellent performance, well above average."


def load_scores() -> dict:
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_scores(scores: dict) -> None:
    try:
        with open(SCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError:
        pass  # saving is optional; the app must never crash because of it


# ----------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------
def pick_font(candidates, fallback="TkDefaultFont"):
    """Return the first installed font family from the list."""
    installed = set(tkfont.families())
    for name in candidates:
        if name in installed:
            return name
    return fallback


class TypingTester:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Typing Speed Tester")
        root.configure(bg=BG)
        root.geometry("900x720")
        root.minsize(820, 680)

        # Fonts
        self.ui_font = pick_font(["Segoe UI", "Helvetica Neue", "Calibri", "Arial", "DejaVu Sans"])
        self.text_font = pick_font(["Consolas", "Menlo", "Courier New", "DejaVu Sans Mono"])

        # State
        self.level = tk.StringVar(value="Easy")
        self.scores = load_scores()
        self.sample = ""
        self.last_sample = None
        self.start_time = None
        self.running = False
        self.finished = False
        self.timer_job = None

        self.setup_styles()
        self.build_header()
        self.build_controls()
        self.build_sample_card()
        self.build_typing_card()
        self.build_metrics()
        self.build_result_card()
        self.build_status_bar()

        root.bind("<Control-r>", lambda e: self.reset())
        self.reset()

    # ---------- Styling ----------
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Accent.TButton", background=ACCENT, foreground="white",
                        font=(self.ui_font, 10, "bold"), padding=(18, 8), borderwidth=0)
        style.map("Accent.TButton",
                  background=[("active", ACCENT_DARK), ("pressed", ACCENT_DARK)])
        style.configure("Plain.TButton", background=CARD, foreground=TEXT,
                        font=(self.ui_font, 10), padding=(18, 8),
                        bordercolor=BORDER, borderwidth=1)
        style.map("Plain.TButton",
                  background=[("active", "#E8ECF3"), ("pressed", "#DDE3EE")])
        style.configure("Bar.Horizontal.TProgressbar", troughcolor="#DFE5EF",
                        background=ACCENT, bordercolor=BG, lightcolor=ACCENT,
                        darkcolor=ACCENT, thickness=8)
        style.configure("TCombobox", padding=4)

    # ---------- Layout ----------
    def build_header(self):
        bar = tk.Frame(self.root, bg=HEADER)
        bar.pack(fill="x")
        tk.Label(bar, text="Typing Speed Tester", bg=HEADER, fg="white",
                 font=(self.ui_font, 20, "bold")).pack(anchor="w", padx=32, pady=(18, 0))
        tk.Label(bar, text="Measure your speed (WPM), accuracy and errors",
                 bg=HEADER, fg="#A9B8D0",
                 font=(self.ui_font, 10)).pack(anchor="w", padx=32, pady=(0, 16))
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

    def build_controls(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=32, pady=(18, 8))

        tk.Label(bar, text="Difficulty", bg=BG, fg=MUTED,
                 font=(self.ui_font, 10)).pack(side="left")
        combo = ttk.Combobox(bar, textvariable=self.level, state="readonly", width=10,
                             values=list(SAMPLES.keys()), font=(self.ui_font, 10))
        combo.pack(side="left", padx=(8, 0))
        combo.bind("<<ComboboxSelected>>", lambda e: self.reset())

        # Buttons are packed from the right edge
        ttk.Button(bar, text="New Text", style="Plain.TButton",
                   command=self.reset).pack(side="right", padx=(8, 0))
        ttk.Button(bar, text="Finish", style="Plain.TButton",
                   command=self.finish).pack(side="right", padx=(8, 0))
        ttk.Button(bar, text="Start", style="Accent.TButton",
                   command=self.start).pack(side="right")

    def make_card(self, title):
        """Create a white bordered card with a small caption and return its body."""
        outer = tk.Frame(self.root, bg=BORDER, padx=1, pady=1)
        outer.pack(fill="x", padx=32, pady=6)
        body = tk.Frame(outer, bg=CARD)
        body.pack(fill="x")
        tk.Label(body, text=title.upper(), bg=CARD, fg=MUTED,
                 font=(self.ui_font, 8, "bold")).pack(anchor="w", padx=16, pady=(12, 0))
        return body

    def build_sample_card(self):
        body = self.make_card("Text to type")
        self.sample_box = tk.Text(body, height=3, wrap="word", bg=CARD, bd=0,
                                  font=(self.text_font, 15), padx=16, pady=10,
                                  cursor="arrow", highlightthickness=0, spacing2=4)
        self.sample_box.pack(fill="x", pady=(0, 8))
        self.sample_box.tag_config("pending", foreground="#7B8494")
        self.sample_box.tag_config("correct", foreground=CORRECT)
        self.sample_box.tag_config("wrong", foreground=WRONG, background=WRONG_BG)
        self.sample_box.tag_config("current", foreground=TEXT, background=CURRENT_BG)
        self.sample_box.config(state="disabled")

    def build_typing_card(self):
        body = self.make_card("Your input")
        self.entry = tk.Text(body, height=4, wrap="word", bg="#FAFBFD", bd=0,
                             font=(self.text_font, 14), padx=16, pady=10,
                             insertbackground=ACCENT, highlightthickness=1,
                             highlightbackground=BORDER, highlightcolor=ACCENT,
                             fg=TEXT, spacing2=4)
        self.entry.pack(fill="x", padx=16, pady=(6, 16))
        self.entry.bind("<KeyPress>", self.on_key_press)
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<Return>", self.on_return)

    def build_metrics(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=32, pady=(10, 4))
        for col in range(5):
            row.columnconfigure(col, weight=1, uniform="m")
        self.time_lbl = self.metric(row, "TIME", 0)
        self.wpm_lbl = self.metric(row, "SPEED (WPM)", 1)
        self.acc_lbl = self.metric(row, "ACCURACY", 2)
        self.err_lbl = self.metric(row, "ERRORS", 3)
        self.best_lbl = self.metric(row, "BEST (LEVEL)", 4)

        self.progress = ttk.Progressbar(self.root, mode="determinate", maximum=100,
                                        style="Bar.Horizontal.TProgressbar")
        self.progress.pack(fill="x", padx=32, pady=(10, 4))

    def metric(self, parent, title, col):
        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.grid(row=0, column=col, sticky="ew", padx=4)
        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both")
        tk.Label(inner, text=title, bg=CARD, fg=MUTED,
                 font=(self.ui_font, 8, "bold")).pack(pady=(10, 0))
        lbl = tk.Label(inner, text="-", bg=CARD, fg=TEXT,
                       font=(self.ui_font, 18, "bold"))
        lbl.pack(pady=(0, 10))
        return lbl

    def build_result_card(self):
        body = self.make_card("Performance report")
        self.grade_lbl = tk.Label(body, text="", bg=CARD, fg=ACCENT,
                                  font=(self.ui_font, 14, "bold"))
        self.grade_lbl.pack(anchor="w", padx=16, pady=(4, 0))
        self.result_lbl = tk.Label(body, text="", bg=CARD, fg=TEXT,
                                   font=(self.ui_font, 10), justify="left")
        self.result_lbl.pack(anchor="w", padx=16, pady=(2, 14))

    def build_status_bar(self):
        bar = tk.Frame(self.root, bg=HEADER)
        bar.pack(side="bottom", fill="x")
        self.status = tk.Label(bar, text="", bg=HEADER, fg="#C5D0E3",
                               font=(self.ui_font, 9), anchor="w")
        self.status.pack(side="left", padx=32, pady=6)
        tk.Label(bar, text="Enter: finish    Ctrl+R: new text", bg=HEADER, fg="#8FA0BC",
                 font=(self.ui_font, 9)).pack(side="right", padx=32)

    # ---------- Core behaviour ----------
    def pick_sample(self):
        options = SAMPLES[self.level.get()]
        choices = [s for s in options if s != self.last_sample] or options
        self.sample = random.choice(choices)
        self.last_sample = self.sample

    def reset(self):
        self.cancel_timer()
        self.running = False
        self.finished = False
        self.start_time = None
        self.pick_sample()

        self.entry.config(state="normal")
        self.entry.delete("1.0", tk.END)

        self.time_lbl.config(text="0.0 s")
        self.wpm_lbl.config(text="0")
        self.acc_lbl.config(text="100%")
        self.err_lbl.config(text="0")
        self.progress["value"] = 0
        self.grade_lbl.config(text="")
        self.result_lbl.config(text="Complete a test to see your results here.", fg=MUTED)
        self.set_status("Ready. Click the input box and begin typing; the timer starts automatically.")
        self.refresh_best()
        self.render_sample("")

    def start(self):
        """Prepare a fresh attempt and place the cursor in the input box."""
        if self.finished or self.running:
            self.reset()
        self.entry.focus_set()
        self.set_status("Waiting for your first keystroke...")

    def set_status(self, text):
        self.status.config(text=text)

    def get_typed(self) -> str:
        return self.entry.get("1.0", "end-1c").replace("\n", " ")

    def on_key_press(self, event):
        if self.finished:
            return "break"
        # The clock starts on the first printable character
        if not self.running and len(event.char) == 1 and event.char.isprintable():
            self.running = True
            self.start_time = time.time()
            self.set_status("Test in progress...")
            self.tick()

    def on_return(self, event):
        """Enter ends the test instead of inserting a new line."""
        if self.running and not self.finished:
            self.finish()
        return "break"

    def on_key_release(self, event):
        if self.finished:
            return
        self.update_live_display()

    def update_live_display(self):
        typed = self.get_typed()
        self.render_sample(typed)
        self.progress["value"] = min(100, len(typed) / max(len(self.sample), 1) * 100)
        self.acc_lbl.config(text=f"{calculate_live_accuracy(self.sample, typed):.0f}%")
        self.err_lbl.config(text=str(count_errors(self.sample[:len(typed)], typed)))

    def render_sample(self, typed: str):
        """Colour the sample text character by character."""
        box = self.sample_box
        box.config(state="normal")
        box.delete("1.0", tk.END)
        for i, ch in enumerate(self.sample):
            if i < len(typed):
                tag = "correct" if typed[i] == ch else "wrong"
            elif i == len(typed) and not self.finished:
                tag = "current"
            else:
                tag = "pending"
            box.insert(tk.END, ch, tag)
        box.config(state="disabled")

    def tick(self):
        if not self.running:
            return
        elapsed = time.time() - self.start_time
        self.time_lbl.config(text=f"{elapsed:.1f} s")
        if elapsed >= 1:
            wpm = calculate_wpm(self.get_typed(), elapsed)
            self.wpm_lbl.config(text=f"{wpm:.0f}")
        self.timer_job = self.root.after(100, self.tick)

    def cancel_timer(self):
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def finish(self):
        if not self.running or self.finished:
            self.set_status("Start typing first, then press Finish (or Enter).")
            return
        elapsed = time.time() - self.start_time
        self.running = False
        self.finished = True
        self.cancel_timer()

        typed = self.get_typed().strip()
        errors = count_errors(self.sample, typed)
        accuracy = calculate_accuracy(self.sample, errors)
        wpm = calculate_wpm(typed, elapsed)

        # Update metric cards with the final values
        self.time_lbl.config(text=f"{elapsed:.1f} s")
        self.wpm_lbl.config(text=f"{wpm:.0f}")
        self.acc_lbl.config(text=f"{accuracy:.0f}%")
        self.err_lbl.config(text=str(errors))
        self.progress["value"] = 100
        self.render_sample(typed)
        self.entry.config(state="disabled")

        grade, feedback = get_rating(wpm, accuracy)
        new_best = self.update_best(wpm, accuracy)
        self.grade_lbl.config(text=f"Grade: {grade}")
        self.result_lbl.config(
            fg=TEXT,
            text=(f"Speed: {wpm:.1f} WPM    Accuracy: {accuracy:.1f}%    "
                  f"Errors: {errors}    Time: {elapsed:.1f} s\n{feedback}"
                  + ("\nNew personal best for this level." if new_best else "")))
        self.refresh_best()
        self.set_status("Test complete. Press New Text (or Ctrl+R) to try again.")

    # ---------- Best score handling ----------
    def update_best(self, wpm: float, accuracy: float) -> bool:
        if accuracy < 70:  # careless attempts do not count as records
            return False
        level = self.level.get()
        if wpm > self.scores.get(level, 0):
            self.scores[level] = round(wpm, 1)
            save_scores(self.scores)
            return True
        return False

    def refresh_best(self):
        best = self.scores.get(self.level.get())
        self.best_lbl.config(text=f"{best:.0f} WPM" if best else "-")


def main():
    root = tk.Tk() #creates the main window
    TypingTester(root) #creates the application window
    root.mainloop() #starts the GUI event loop


if __name__ == "__main__":
    main()