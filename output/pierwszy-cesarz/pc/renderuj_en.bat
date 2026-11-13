@echo off
rem The First Emperor - render 1440p PO AKCEPTACJI w Studio: klipy ujec -> film z lektorem (bez muzyki i efektow).
rem Przerwany render mozna uruchomic ponownie: gotowe klipy zostaja.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
set JEZYK=en
set ROZDZIELCZOSC=1440
set PYTHONIOENCODING=utf-8
if not defined PROCESY set PROCESY=4
if not defined KLIPY set KLIPY=klipy_en_1440p_turbo
set "PY=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
echo [1/2] Klipy 1440p (PROCESY=%PROCESY%) do %KLIPY%...
"%PY%" -I output\pierwszy-cesarz\render.py klipy %KLIPY% || (pause & exit /b 1)
echo [2/2] Film z lektorem...
"%PY%" -I output\pierwszy-cesarz\zloz.py %KLIPY% The_First_Emperor_1440p_turbo.mp4 || (pause & exit /b 1)
echo Gotowe: The_First_Emperor_1440p_turbo.mp4
pause
