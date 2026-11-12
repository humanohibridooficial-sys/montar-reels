@echo off
rem Doble clic: abre Claude Code en esta carpeta. Luego le dices "edita este reel".
cd /d "%~dp0"
where claude >nul 2>nul
if errorlevel 1 (
  echo No encuentro Claude Code. Haz doble clic primero en 1 INSTALAR.bat.
  pause
  exit /b 1
)
claude
