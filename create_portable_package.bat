@echo off
echo Creating portable OpenShift GUI package...

REM Check for the OpenShiftGUI directory in dist
if not exist "dist\OpenShiftGUI" (
  echo ERROR: OpenShiftGUI directory not found in dist folder!
  echo Please run build.bat first to create the executable.
  echo.
  pause
  exit /b 1
)

REM Create a directory for the portable package
mkdir "OpenShiftGUI-Portable" 2>nul
echo Cleaning previous package contents...
del /S /Q "OpenShiftGUI-Portable\*" 2>nul

REM Copy the entire application directory
echo Copying application files...
xcopy "dist\OpenShiftGUI\*" "OpenShiftGUI-Portable\" /E /I /Y

REM Create a readme file for the portable package
echo Creating documentation files...
echo OpenShift GUI - Portable Edition > "OpenShiftGUI-Portable\README.txt"
echo. >> "OpenShiftGUI-Portable\README.txt"
echo Instructions: >> "OpenShiftGUI-Portable\README.txt"
echo 1. Download the OpenShift CLI (oc.exe) if you haven't already >> "OpenShiftGUI-Portable\README.txt"
echo 2. Run OpenShiftGUI.exe >> "OpenShiftGUI-Portable\README.txt"
echo 3. Go to Settings -^> Preferences and set the path to your oc.exe file >> "OpenShiftGUI-Portable\README.txt"
echo. >> "OpenShiftGUI-Portable\README.txt"
echo That's it! You can now use OpenShift GUI to manage your OpenShift clusters. >> "OpenShiftGUI-Portable\README.txt"

REM Create oc.exe folder
mkdir "OpenShiftGUI-Portable\oc-cli" 2>nul
echo This folder is where you can place your oc.exe file > "OpenShiftGUI-Portable\oc-cli\README.txt"
echo (optional - you can also specify a path to oc.exe anywhere on your system) >> "OpenShiftGUI-Portable\oc-cli\README.txt"

REM Create a batch file that can automatically find oc.exe in the same folder
echo @echo off > "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo REM This batch file will automatically use an oc.exe file if placed in the oc-cli folder >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo. >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo set "OC_PATH=%%~dp0oc-cli\oc.exe" >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo. >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo if exist "%%OC_PATH%%" ( >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo   echo Found oc.exe in oc-cli folder. Launching OpenShiftGUI... >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo ) else ( >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo   echo oc.exe not found in oc-cli folder. >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo   echo You will need to configure the path manually in Settings. >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo   timeout /t 3 >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo ) >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo. >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"
echo start "" "OpenShiftGUI.exe" >> "OpenShiftGUI-Portable\RunWithLocalOC.bat"

echo.
echo Portable package created in the "OpenShiftGUI-Portable" folder.
echo.
echo Package ready for distribution to users. You can zip this folder and share it.
echo.
pause