@echo off
rem Syn słońca - krok 2: render wszystkich ujęć w pełnej jakości (1280x720, 24 kl./s) do folderu "klipy" w repozytorium.
rem Przerwany render można uruchomić ponownie: gotowe klipy zostają, liczy się tylko reszta.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
where ffmpeg >nul 2>nul || (echo Brak ffmpeg w PATH. Zainstaluj: winget install Gyan.FFmpeg i otwórz nowe okno. & pause & exit /b 1)
python -m pip install --quiet --user numpy pillow
for /f %%n in ('dir /b output\powstanie-japonii\lektor\*.json ^| find /c /v ""') do set LEKTOR=%%n
if %LEKTOR% LSS 68 (echo Lektor ma dopiero %LEKTOR% z 68 kwestii. Najpierw nagraj_lektora.bat - dlugosci ujec biora sie z nagran. & pause & exit /b 1)
if not defined PROCESY set PROCESY=4
python output\powstanie-japonii\render.py klipy klipy
rem muzyka i efekty od nowa: ich czasy zależą od długości nagranych kwestii
python output\powstanie-japonii\efekty.py
echo.
echo Gotowe. Przenieś na Maca foldery "klipy", "output\powstanie-japonii\lektor" i "output\powstanie-japonii\dzwiek".
pause
