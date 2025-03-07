import os
import sys
import PyInstaller
from PyInstaller.utils.hooks import collect_all

# Collect all dependencies for PySide6
datas, binaries, hiddenimports = collect_all('PySide6')

# This will help debug any issues with the PyInstaller process
print("PySide6 hiddenimports:", hiddenimports)
print("PySide6 binaries:", binaries)