@echo off
rem Doble clic y listo: instala todo lo que necesita el editor. Se puede repetir; lo que ya esta, lo salta.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0instalar.ps1"
echo.
echo Si arriba pone "Todo listo", ya puedes abrir 2 EDITAR.bat.
echo Si pone que cierres la ventana, cierrala y vuelve a hacer doble clic en 1 INSTALAR.bat.
pause
