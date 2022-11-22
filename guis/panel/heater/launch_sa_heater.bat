@ECHO OFF
cls

SETLOCAL
set /p "panel=Input three-digit panel number> "
CD C:\Users\%USERNAME%\Desktop\Production
python -m guis.panel.heater %panel%
ENDLOCAL
