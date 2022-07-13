@ECHO OFF
cls
CD C:\Users\%USERNAME%\Desktop\Production

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

python -m guis.straw.consolidate.find_pmf
pause
