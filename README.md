<div align="center">

# AirClick

Gesture-controlled interaction suite: AI Virtual Mouse, Gesture Space Shooter, and Hand Sign Language Recognizer.

</div>

## Overview

AirClick is a small gesture-controlled interaction toolkit built on top of OpenCV, MediaPipe, and Pygame. It lets you:

- Control your mouse using hand gestures (AI Virtual Mouse)
- Play a gesture-enabled Space Shooter game
- Type simple text using hand-sign patterns

Everything runs locally using your webcam. No data is sent to external servers.

## Modules in this repository

- `Virtual_Mouse.py` — AI Virtual Mouse + app launcher
- `HandTrackingModule2.py` — MediaPipe-based hand tracking helper used by other modules
- `gesture.py` — Gesture controls for the Space Shooter
- `main.py` — Space Shooter game (Pygame) with gesture + keyboard input
- `sign_language.py` — Simple hand sign language typing tool

There is **no Voice Band / music module** in this repository, and there are **no `main2.py` or `gesture2.py` files**.

## Requirements

- A computer with a webcam
- Python 3.10 or 3.11
- Dependencies from `requirements.txt` (OpenCV, MediaPipe, Pygame, NumPy, etc.)

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Quick start

### 1) AI Virtual Mouse (`Virtual_Mouse.py`)

Run:

```bash
python Virtual_Mouse.py
```

Features:

- Move cursor by moving your index finger inside a control rectangle
- Drag & drop using the pinky while moving
- Left click via an index–middle finger pinch
- Right click with a specific finger pattern
- Scroll with thumb/pinky-only gestures
- Long-hold gestures to launch other modules:
  - Open palm (all fingers up) — launch Space Shooter (`main.py`)
  - Index + pinky up (others down) — launch Hand Sign Language (`sign_language.py`)

Key parameters in `Virtual_Mouse.py`:

- `wCam, hCam` — camera resolution (default 640×480)
- `frameR` — margin for the on-screen control area
- `smoothening` — mouse movement smoothing factor
- `launch_hold_time` — hold duration (seconds) to trigger app launch
- `screen_width, screen_height` — your display resolution (used for mapping)

### 2) Space Shooter (`main.py`)

Run:

```bash
python main.py
```

Summary:

- 2D Pygame space shooter with enemies, waves, and a boss
- Player ship with health bar and power-ups (health, shield, rapid fire)
- Basic explosion and laser sound effects

Controls:

- **Gestures** (via `gesture.py`):
  - Move left/right by moving your index finger horizontally
  - Fire when thumb and index finger pinch together
- **Keyboard**:
  - Left / Right arrows — horizontal movement
  - Up / Down arrows — vertical movement
  - Space — fire

The game window can be closed normally. On exit, it attempts to release any active camera resources via `release_camera()` from `gesture.py`.

### 3) Hand Sign Language (`sign_language.py`)

Run:

```bash
python sign_language.py
```

Summary:

- Uses `HandTrackingModule2.py` to detect whether each finger is up or down
- Maps simple finger patterns to letters A–Z and space
- Shows:
  - Current detected letter
  - Accumulated text (last ~30 characters)
  - Basic instructions overlayed on the camera feed

Usage:

- Hold a gesture steady for `SAVE_TIME` seconds (default 1s) to confirm a letter
- Press `c` to clear the text
- Press `q` to quit

## Project structure

```text
AirClick/
├─ Virtual_Mouse.py           # AI Virtual Mouse + launcher
├─ HandTrackingModule2.py     # Hand tracking helper (MediaPipe wrapper)
├─ gesture.py                 # Gesture recognition for Space Shooter
├─ main.py                    # Space Shooter game (Pygame)
├─ sign_language.py           # Hand Sign Language typing
├─ assets/                    # (if present) images / UI assets for the game
├─ sounds/                    # (if present) sound assets for the game
├─ requirements.txt           # Python dependencies
└─ venv_py311/                # (optional) virtual environment, not required to run
```

## Tips & troubleshooting

- **Webcam not detected**
  - Close other apps using the camera.
  - If needed, change the camera index in `cv2.VideoCapture(0)` to `1`, `2`, etc.

- **Tracking is unstable / jittery**
  - Improve lighting and use a plain background.
  - Increase `smoothening` or adjust the control rectangle (`frameR`).

- **Cursor moves in the opposite direction**
  - In `Virtual_Mouse.py`, the X-coordinate is mirrored using `screen_width - x`. Adjust this mapping if your camera setup requires different behavior.

- **Dependencies fail to install**
  - Upgrade pip: `python -m pip install --upgrade pip`
  - Then reinstall: `pip install -r requirements.txt`

## License

MIT — see `LICENSE` if provided in this repository.

## Credits

- OpenCV, MediaPipe, NumPy
- Pygame
- pynput, PyAutoGUI

## Privacy

All processing runs entirely on your local machine. The webcam stream is used only for real-time control and is not transmitted or stored remotely.