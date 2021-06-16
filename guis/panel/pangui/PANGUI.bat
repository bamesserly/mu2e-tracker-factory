@ECHO OFF
cls

CD C:\Users\%USERNAME%\Desktop\Production\

REM=============================================================================
REM Run a software update once-per-day
REM=============================================================================
set CUR_YYYY=%date:~10,4%
set CUR_MM=%date:~4,2%
set CUR_DD=%date:~7,2%
set SUBFILENAME=C:\Users\mu2e\Desktop\MergeDownLogs\Updater_%CUR_YYYY%%CUR_MM%%CUR_DD%*
if not exist %SUBFILENAME% (
	echo Running software update!
	call Updater.bat
)
REM else (
REM echo Not running software update
REM )

REM=============================================================================
REM Run the GUI
REM=============================================================================
python -m guis.panel.pangui

REM dir /s "logfiles\%SUBFILENAME*.txt"
REM echo %SUBFILENAME%
