@echo off
echo Building OpenShift GUI...

REM Clean up previous build artifacts
echo Cleaning up previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "venv_build" rmdir /s /q "venv_build"

REM Create a virtual environment for building
echo Creating virtual environment for reliable building...
python -m venv venv_build
call venv_build\Scripts\activate.bat

REM Install required packages with specific versions in the virtual environment
echo Installing dependencies...
pip install -r requirements.txt

REM Generate icon file if it doesn't exist
echo Checking/generating application icon...
python generate_icon.py

REM Create the executable with additional safeguards
echo Creating executable...
pyinstaller --clean --noconfirm ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import keyring.backends.Windows ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  --add-binary "venv_build\Lib\site-packages\PySide6\plugins\*;PySide6\plugins" ^
  --add-binary "venv_build\Lib\site-packages\shiboken6\*;shiboken6" ^
  --icon=app\resources\icon.ico ^
  --noconsole ^
  --name OpenShiftGUI ^
  main.py

REM Also create a debug version with console
echo Creating debug version with console...
pyinstaller --clean --noconfirm ^
  --hidden-import PySide6.QtCore ^
  --hidden-import PySide6.QtGui ^
  --hidden-import PySide6.QtWidgets ^
  --hidden-import keyring.backends.Windows ^
  --collect-all PySide6 ^
  --collect-all shiboken6 ^
  --add-binary "venv_build\Lib\site-packages\PySide6\plugins\*;PySide6\plugins" ^
  --add-binary "venv_build\Lib\site-packages\shiboken6\*;shiboken6" ^
  --icon=app\resources\icon.ico ^
  --name OpenShiftGUI_debug ^
  main.py

REM Deactivate virtual environment
call venv_build\Scripts\deactivate.bat

echo.
if exist "dist\OpenShiftGUI\OpenShiftGUI.exe" (
    echo Build complete!
    echo The executable can be found in the "dist\OpenShiftGUI" folder.
    echo The debug version with console output is in "dist\OpenShiftGUI_debug" folder.
) else (
    echo Build failed! Please check the error messages above.
)
echo.
pause