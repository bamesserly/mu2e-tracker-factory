@ECHO OFF

REM Script that updates Desktop/Production with the latest PANGUI code

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
call :sub > C:\Users\%USERNAME%\Desktop\MergeDownLogs\Updater_%SUBFILENAME%.txt
exit /b

REM=============================================================================
REM Define the sub command: just fetch and pull
REM=============================================================================
:sub
cd C:\Users\Mu2e\Desktop\Production
git status
git fetch --tags
git fetch
REM This next, stupid-looking line is how we set the output of the git command
REM to the variable latesttag.
REM The git command, by the way, gets the latest tag.
FOR /F "tokens=* USEBACKQ" %%g IN (`git tag --sort=v:refname`) DO (SET latesttag=%%g)
echo Checking out latest tag %latesttag%
git checkout %latesttag%
git status
