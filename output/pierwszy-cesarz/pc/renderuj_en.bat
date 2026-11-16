@echo off
rem The First Emperor - render koncowy 1440p PO AKCEPTACJI w Studio: klipy ujec -> gotowy film na YouTube
rem (obraz, lektor, muzyka i efekty zmiksowane jak montaz w Studio).
rem Przed renderem: lektor_en\*.wav i dzwiek_en\*.wav z Maca (nie ma ich na GitHubie) - patrz CZYTAJ.txt.
rem Przerwany render mozna uruchomic ponownie: gotowe klipy zostaja.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
set JEZYK=en
set ROZDZIELCZOSC=1440
rem render koncowy: dokladne kodowanie x264 (render.py domyslnie koduje veryfast - do przegladu w Studio)
set PRESET=slow
rem klatki ujec na siatce czasu filmu: film trwa tyle co os w Studio, muzyka i efekty nie rozjezdzaja sie z obrazem
set FILM=1
set PYTHONIOENCODING=utf-8
if not defined PROCESY set PROCESY=4
rem ten sam katalog co poprzedni render 1440p: ujecia z tym samym odciskiem (kod, swiat, liczba klatek...) zostaja
if not defined KLIPY set KLIPY=klipy_en_1440p_turbo
set "PY=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
echo [1/3] Czy lektor, muzyka i efekty sa z tej wersji filmu...
"%PY%" -I output\pierwszy-cesarz\zloz.py --sprawdz || (echo Skopiuj z Maca paczke dzwieku - patrz CZYTAJ.txt. & pause & exit /b 1)
echo [2/3] Klipy 1440p (PROCESY=%PROCESY%) do %KLIPY%...
"%PY%" -I output\pierwszy-cesarz\render.py klipy %KLIPY% || (pause & exit /b 1)
echo [3/3] Film: obraz, lektor, muzyka i efekty...
"%PY%" -I output\pierwszy-cesarz\zloz.py %KLIPY% The_First_Emperor_1440p_YouTube.mp4 || (pause & exit /b 1)
echo Gotowe: The_First_Emperor_1440p_YouTube.mp4
pause
