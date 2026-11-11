@echo off
rem Pierwszy cesarz - krok 2: render wszystkich ujęć w pełnej jakości (1280x720, 24 kl./s) do folderu "klipy" w repozytorium.
rem Przerwany render można uruchomić ponownie: gotowe klipy zostają, liczy się tylko reszta.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
where ffmpeg >nul 2>nul || (echo Brak ffmpeg w PATH. Zainstaluj: winget install Gyan.FFmpeg i otwórz nowe okno. & pause & exit /b 1)
python -m pip install --quiet --user numpy pillow
for /f %%n in ('dir /b output\pierwszy-cesarz\lektor\*.json ^| find /c /v ""') do set LEKTOR=%%n
if %LEKTOR% LSS 67 (echo Lektor ma dopiero %LEKTOR% z 67 kwestii. Najpierw nagraj_lektora.bat - dlugosci ujec biora sie z nagran. & pause & exit /b 1)
if not defined PROCESY set PROCESY=4
python output\pierwszy-cesarz\render.py klipy klipy
rem muzyka i efekty od nowa: ich czasy zależą od długości nagranych kwestii
python output\pierwszy-cesarz\efekty.py
echo.
echo Gotowe. Przenieś na Maca foldery "klipy", "output\pierwszy-cesarz\lektor" i "output\pierwszy-cesarz\dzwiek".
pause
