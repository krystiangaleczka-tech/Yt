@echo off
rem The First Emperor (EN) - lektor nagrany OD NOWA przepisem teatru papierowego (Podrecznik pracowni - Lektor, zasada 8):
rem Chatterbox Multilingual z ustawieniami TEATR (exaggeration 1,0 / cfg 0,3 / temperature 0,7 - mocna ekspresja),
rem tekst bez znacznikow emocji, probka bez poglosu ref_en_studio.wav, 3 podejscia na kwestie (42/7/123), kazde sprawdza
rem Whisper, wybor z oddechem na przecinkach, potem 3% wolniej i pauzy losowane z zakresow (lektor_studio.py podejscia --teatr).
rem Potem muzyka i efekty pod nowe dlugosci. Studio: zobacz ostatni krok na dole.
rem Gotowe podejscia zostaja (ten sam tekst, silnik i probka), wiec przerwane nagrywanie wznawia sie od miejsca przerwania.
rem Obecny lektor (Turbo z emocjami, 3% wolniej i pauzy) zostaje w kopii: output\pierwszy-cesarz\lektor_en_turbo.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
set JEZYK=en
set SILNIK=chatterbox
set TEATR=1
set "PROMPT=%CD%\pilot\assets\ref_en_studio.wav"
set "PROBKA=%PROMPT%"
set PYTHONIOENCODING=utf-8
set "TTS=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
if not defined LEKTOR_ENHANCE set "LEKTOR_ENHANCE=%CD%\.venv-enhance\Scripts\python.exe"
if not exist "%LEKTOR_ENHANCE%" (echo Brak .venv-enhance - uruchom najpierw zrob_film_en.bat, ktory je tworzy. & pause & exit /b 1)
if not exist "%PROMPT%" (echo Brak probki pilot\assets\ref_en_studio.wav - przenies ja z Maca osobno, nie ma jej na GitHubie. & pause & exit /b 1)

if exist "output\pierwszy-cesarz\lektor_en_turbo" goto nagraj
echo Kopia obecnego lektora (Turbo) do output\pierwszy-cesarz\lektor_en_turbo...
xcopy /e /i /q "output\pierwszy-cesarz\lektor_en" "output\pierwszy-cesarz\lektor_en_turbo" >nul
rmdir /s /q "output\pierwszy-cesarz\lektor_en"
mkdir "output\pierwszy-cesarz\lektor_en"

:nagraj
set HF_HUB_OFFLINE=1
echo [1/2] Lektor: 3 podejscia na kwestie (Multilingual, TEATR), Whisper, obrobka, 3%% wolniej i pauzy...
"%TTS%" -I output\pierwszy-cesarz\lektor_en.py || (echo Nagrywanie przerwane - uruchom jeszcze raz, gotowe podejscia zostaja. & pause & exit /b 1)
echo [2/2] Muzyka i efekty pod dlugosci nagran (output\pierwszy-cesarz\dzwiek_en)...
"%TTS%" -I output\pierwszy-cesarz\efekty.py || (pause & exit /b 1)
echo.
echo Gotowe. Do Studio (projekt EN, Studio dziala): przenies lektor_en i dzwiek_en na Maca albo na PC uruchom:
echo   "%TTS%" -I output\pierwszy-cesarz\studio_pc.py --port 3000 --projekt prj_65a9a00a6f9d402c --aktualizuj --stopklatka --lektor --klipy build\klipy_en_zapas
echo Inne podejscie kwestii: output\pierwszy-cesarz\lektor_en\podejscia\wybor.json, potem lektor_studio.py podejscia ... --teatr
pause
