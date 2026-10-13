# Deployment

## Build the Windows version

From the project folder, with the virtual environment active:

    pip install pyinstaller
    python scripts\build_windows.py 1.0.0

This creates `dist\PythonAdventure\PythonAdventure.exe` and the ZIP `dist\PythonAdventure-v1.0.0-windows.zip`.

The build uses `--onedir` (a folder) because it starts faster and triggers fewer antivirus warnings than a single-file build. The `levels` folder is bundled with `--add-data`.

## Checking a build

1. Extract the ZIP into a new folder, away from the project.
2. Run `PythonAdventure.exe`.
3. Check the menu, Play, Level Select, sound and the saved Best score.
4. Ideally also test on a second PC without Python installed.

## Limits

- The build is not code-signed, so Windows SmartScreen shows a warning.
- It was built on Windows and works only on Windows.
- macOS and browser versions are separate steps.
