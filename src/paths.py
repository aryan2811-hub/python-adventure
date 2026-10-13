import os
import sys


def base_dir():
    """Project folder when running from source, or the temp bundle folder inside a PyInstaller build."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(*parts):
    return os.path.join(base_dir(), *parts)
