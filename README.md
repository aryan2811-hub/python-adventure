# Python Adventure

A 2D side-scrolling platformer made with Python and Pygame. Run, jump, collect coins, stomp enemies, and beat three levels.

## Screenshots

(Add 2 or 3 screenshots of the real game here.)

## Features

- Three levels, from beginner to a final boss
- Walking and flying enemies, moving and breakable platforms, checkpoints
- Five hearts of health and a scoring system
- Sound effects and music generated in code
- Particle effects
- Main menu, pause menu, settings, level select, instructions
- Saved high score, unlocked levels and sound settings
- Fullscreen with F11

## Controls

See docs/CONTROLS.md. Short version: A/D or arrows to move, Space to jump, Esc to pause, M to mute, F11 for fullscreen.

## Run from source

Requires Python 3.

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

## Run the tests

    python -m pytest -q

## Where your progress is saved

Windows: %APPDATA%\PythonAdventure\save.json. Delete that file to reset your progress.

## Known limitations

- A downloadable Windows build and a browser version are planned but not finished yet.
- No macOS build yet.

## Troubleshooting

- No sound: check your Windows output device. The game keeps running without sound if no audio device is found.
- Broken save: delete save.json and the game starts fresh.

## Credits and licenses

- Code: MIT License (see LICENSE).
- Graphics: drawn in code, no external image files.
- Sound and music: generated in code, no external audio files.
- Engine: pygame-ce, see its own license.
