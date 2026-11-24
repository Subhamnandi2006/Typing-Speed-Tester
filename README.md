# ⌨️ Typing Speed Tester

A desktop typing speed test built with Python and Tkinter. It measures your **speed (WPM)**, **accuracy (%)** and **number of errors** in real time, and saves your best score for each difficulty level.

## Features

- **Three difficulty levels:** Easy, Medium and Hard, each with 10 sample sentences. Hard includes punctuation, numbers and symbols.
- **Live feedback:** the sample text is coloured character by character as you type (correct, wrong, current, pending).
- **Live metrics:** time, WPM, accuracy and error count update while you type, with a progress bar.
- **Auto-start timer:** the clock starts on your first keystroke.
- **Performance report:** after each test you get a grade (Needs Improvement, Beginner, Intermediate, Proficient or Expert) with short feedback.
- **Personal bests:** the best WPM for each level is saved to `best_scores.json`. Attempts below 70% accuracy don't count as records.
- **No repeats:** the same sentence won't appear twice in a row.

## Requirements

- Python 3.6 or higher
- Tkinter (included with the standard Python installer on Windows and macOS)

No external packages are needed.

On Linux, install Tkinter if it's missing:

```bash
sudo apt install python3-tk
```

## Installation and Usage

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python TypingSpeed.py
```

### How to play

1. Choose a difficulty level.
2. Click the input box and start typing the sample text. The timer starts automatically.
3. Press **Enter** to finish.
4. Check your results in the performance report.
5. Press **New Text** or **Ctrl+R** for another attempt.

### Keyboard shortcuts

| Key      | Action                       |
|----------|------------------------------|
| `Enter`  | Finish the test              |
| `Ctrl+R` | Load a new text / reset      |

## How it's calculated

| Metric   | Formula |
|----------|---------|
| **WPM**      | `(characters typed / 5) / minutes elapsed` (one word = 5 characters) |
| **Errors**   | Wrong, missing and extra characters, compared position by position |
| **Accuracy** | `(sample length − errors) / sample length × 100` |

### Grading

| Grade             | Condition                |
|-------------------|--------------------------|
| Needs Improvement | Accuracy below 70%       |
| Beginner          | Under 20 WPM             |
| Intermediate      | 20–39 WPM                |
| Proficient        | 40–59 WPM                |
| Expert            | 60 WPM and above         |

## Project Structure

```
├── TypingSpeed.py      # Main application (logic + GUI)
├── best_scores.json    # Saved best WPM per level (auto-generated)
└── README.md
```

`best_scores.json` is created and updated automatically. Example:

```json
{
  "Easy": 80.3,
  "Medium": 37.6
}
```

## Code Overview

- **Backend functions** (`count_errors`, `calculate_wpm`, `calculate_accuracy`, `get_rating`, `load_scores`, `save_scores`) are pure functions, independent of the GUI.
- **`TypingTester` class** builds the Tkinter interface and handles the typing session.
- **Modules used:** `tkinter`/`ttk`, `time`, `random`, `json`, `os`.

## Possible Improvements

- Custom text or paragraph input
- Timed mode (30 / 60 seconds)
- History graph of past scores
- Dark mode

## License

This project is open source. Add a license of your choice (e.g. MIT).

## Author

Made by **Subham**
