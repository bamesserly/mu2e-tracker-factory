@ECHO OFF
cls

CD C:\Users\%USERNAME%\Desktop\Production\

REM=============================================================================
REM Run the GUI
REM=============================================================================
python -m tests.get_straw_info
