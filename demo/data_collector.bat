@echo off
REM Run Data Collector
cd /d "%~dp0"
C:\Users\Test\AppData\Local\Programs\Python\Python314\python.exe data_collector.py %*
pause
