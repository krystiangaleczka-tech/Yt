@echo off
rem The First Emperor - wersja angielska: lektor (klon glosu, Chatterbox Turbo ze znacznikami emocji z aktorskie_en.json)
rem -> podglad w DocOS Studio do akceptacji. Render 1440p dopiero po akceptacji: renderuj_en.bat.
rem Gotowe kwestie zostaja (ten sam tekst i silnik), wiec przerwane nagrywanie wznawia sie od miejsca przerwania.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
set JEZYK=en
set SILNIK=turbo
set "AKTORSKIE=%CD%\output\pierwszy-cesarz\aktorskie_en.json"
set "PROMPT=%CD%\pilot\assets\ref_en_prompt.wav"
set "PROBKA=%PROMPT%"
set HF_HUB_OFFLINE=1
set PYTHONIOENCODING=utf-8
set "TTS=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
if not exist "%PROMPT%" (echo Brak probki glosu pilot\assets\ref_en_prompt.wav - nie ma jej na GitHubie, bo repo jest publiczne. & pause & exit /b 1)
echo [1/2] Lektor...
"%TTS%" -I output\pierwszy-cesarz\lektor_en.py || (pause & exit /b 1)
echo [2/2] Podglad w Studio (Studio musi dzialac na porcie 8876)...
"%TTS%" -I output\pierwszy-cesarz\studio_pc.py || (pause & exit /b 1)
echo Obejrzyj w Studio. Po akceptacji: renderuj_en.bat
pause
