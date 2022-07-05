@ECHO OFF
cls

REM Switch to correct folder
REM=============================================================================
CD C:\Users\%USERNAME%\Desktop\production\

REM Run the GUI
REM=============================================================================
python -m guis.panel.partsprep.partsPrepMain
