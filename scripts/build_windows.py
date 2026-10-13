import shutil
import subprocess
import sys

VERSION = sys.argv[1] if len(sys.argv) > 1 else "1.0.0"
NAME = "PythonAdventure"

subprocess.run(
    [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onedir",
     "--windowed", "--name", NAME, "--add-data", "levels;levels", "main.py"],
    check=True,
)
archive = shutil.make_archive("dist/%s-v%s-windows" % (NAME, VERSION), "zip", "dist", NAME)
print("Created", archive)
