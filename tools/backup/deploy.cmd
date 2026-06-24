@echo off
setlocal
cd /d "%~dp0"

REM this is for Windows

rem using the python script:
python deploy.py %*

