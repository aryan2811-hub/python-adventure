# Installation

## Windows (download and play, no Python needed)

1. Download `PythonAdventure-v1.0.0-windows.zip` from the GitHub Releases page.
2. Right-click the ZIP and choose **Extract All**. Do not run the game from inside the ZIP.
3. Open the extracted `PythonAdventure` folder.
4. Double-click `PythonAdventure.exe`.

Keep the whole folder together. The `.exe` needs the files next to it.

### Windows security warnings

The game is not code-signed (a certificate costs money), so Windows may show **Windows protected your PC**.

- Click **More info**, then **Run anyway**.
- Only do this if you got the file from the person who made it or from the official GitHub release.
- Some antivirus programs wrongly flag apps made with PyInstaller. The full source code is public in the repository, and you can build the game yourself.
- To check your download is unchanged, run `Get-FileHash PythonAdventure-v1.0.0-windows.zip` in PowerShell and compare it with the SHA256 value in the release notes.

### Where progress is saved

`%APPDATA%\PythonAdventure\save.json`. Delete that file to reset progress.

## macOS

There is no macOS build yet. A Windows `.exe` does not run on a Mac. Mac users can run the game from source (see README.md) with Python 3 installed.

## Run from source (any system)

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python main.py

On macOS or Linux, activate with `source .venv/bin/activate`.

## Troubleshooting

- Nothing happens when you double-click: extract the ZIP fully first, then try again.
- No sound: check your Windows output device. The game still runs without sound.
- Broken progress: delete `save.json` and start again.
