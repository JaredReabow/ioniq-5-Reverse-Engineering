@echo off
setlocal DisableDelayedExpansion
title Gen5W VM Workbench
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0Gen5W.ps1" %*
set "result=%errorlevel%"
if not "%result%"=="0" pause
exit /b %result%
