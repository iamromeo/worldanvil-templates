@echo off
setlocal
cd /d "%~dp0"

REM this is for Windows

REM example: extract.cmd alana/the-titans_2025-04-17_120213.json
REM example: extract.cmd alana/the-titans_2025-04-17_120213.json -l a -t

rem using the python script:
python extract.py %*
