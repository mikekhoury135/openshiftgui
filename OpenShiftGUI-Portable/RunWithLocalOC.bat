@echo off 
REM This batch file will automatically use an oc.exe file if placed in the oc-cli folder 
 
set "OC_PATH=%~dp0oc-cli\oc.exe" 
 
if exist "%OC_PATH%" ( 
  echo Found oc.exe in oc-cli folder. Launching OpenShiftGUI... 
) else ( 
  echo oc.exe not found in oc-cli folder. 
  echo You will need to configure the path manually in Settings. 
  timeout /t 3 
) 
 
start "" "OpenShiftGUI.exe" 
