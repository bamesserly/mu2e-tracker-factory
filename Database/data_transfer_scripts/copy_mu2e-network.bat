@ECHO OFF

ECHO MERGEDOWN IN PROGRESS.
ECHO DO NOT CLOSE THIS WINDOW.
ECHO WINDOW WILL CLOSE AUTOMATICALLY WHEN MERGEDOWN IS FINISHED.

REM=============================================================================
REM Collect YYYMMDD-HHMMSS int a variable
REM=============================================================================
set CUR_YYYY=%date:~10,4%
set CUR_MM=%date:~4,2%
set CUR_DD=%date:~7,2%
set CUR_HH=%time:~0,2%
if %CUR_HH% lss 10 (set CUR_HH=0%time:~1,1%)
set CUR_NN=%time:~3,2%
set CUR_SS=%time:~6,2%
set CUR_MS=%time:~9,2
set SUBFILENAME=%CUR_YYYY%%CUR_MM%%CUR_DD%-%CUR_HH%%CUR_NN%%CUR_SS% 

REM=============================================================================
REM call the sub command and pass its output to a logfile
REM=============================================================================
call :sub > C:\Users\%USERNAME%\Desktop\MergeDownLogs\mergedown_%SUBFILENAME%.txt
exit /b

REM=============================================================================
REM Define the sub command:
REM First robocopy the network PE DOWN to the lab computer.
REM Then robocopy the lab computer UP to the network.
REM TODO If the first command fails, then we risk overwriting
REM=============================================================================
:sub
robocopy \\spa-mu2e-network\Files\Production_Environment\Data C:\Users\%USERNAME%\Desktop\Production\Data /e
robocopy C:\Users\%USERNAME%\Desktop\Production\Data \\spa-mu2e-network\Files\Production_Environment\Data /e
