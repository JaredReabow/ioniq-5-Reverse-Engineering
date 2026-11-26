@echo off
setlocal DisableDelayedExpansion
title Gen5W VM Workbench
set "no_pause="
for %%a in (%*) do (
    if /I "%%~a"=="-Yes" set "no_pause=1"
    if /I "%%~a"=="-NoPause" set "no_pause=1"
)
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0Gen5W.ps1" %*
set "result=%errorlevel%"
if not "%result%"=="0" if not defined no_pause pause
exit /b %result%
