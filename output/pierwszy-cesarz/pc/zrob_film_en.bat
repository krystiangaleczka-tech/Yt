@echo off
rem The First Emperor - wersja angielska: lektor (klon glosu, Chatterbox Turbo ze znacznikami emocji z aktorskie_en.json)
rem sposobem z Podrecznika pracowni - Lektor: probka bez poglosu, 3 podejscia na kwestie, suche i z odbudowanym pasmem
rem (resemble-enhance), wybor podejscia z oddechami na przecinkach -> muzyka i efekty pod nowe dlugosci -> podglad w DocOS
rem Studio do akceptacji. Render 1440p dopiero po akceptacji: renderuj_en.bat.
rem Gotowe podejscia zostaja (ten sam tekst, silnik i probka), wiec przerwane nagrywanie wznawia sie od miejsca przerwania.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
set JEZYK=en
set SILNIK=turbo
set "AKTORSKIE=%CD%\output\pierwszy-cesarz\aktorskie_en.json"
set "PROMPT=%CD%\pilot\assets\ref_en_studio.wav"
set "PROBKA=%PROMPT%"
set PYTHONIOENCODING=utf-8
set "TTS=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
if not defined KLIPY_STARE set "KLIPY_STARE=%CD%\klipy_en_1440p"

rem srodowisko odbudowy pasma i suchego brzmienia (resemble-enhance) - osobne, inne wersje bibliotek niz Chatterbox
if not defined LEKTOR_ENHANCE set "LEKTOR_ENHANCE=%CD%\.venv-enhance\Scripts\python.exe"
if exist "%LEKTOR_ENHANCE%" goto probka
echo Tworze srodowisko resemble-enhance (jednorazowo, kilka GB: PyTorch z CUDA)...
py -3.11 -m venv .venv-enhance || (echo Potrzebny Python 3.11: winget install Python.Python.3.11 & pause & exit /b 1)
"%LEKTOR_ENHANCE%" -m pip install --upgrade pip
"%LEKTOR_ENHANCE%" -m pip install torch==2.4.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
"%LEKTOR_ENHANCE%" -m pip install resemble-enhance==0.0.1 --no-deps
"%LEKTOR_ENHANCE%" -m pip install -r requirements-enhance.txt

:probka
rem probka bez poglosu z angielskiego nagrania autora (Turbo mowi tylko po angielsku; ref_en.wav nie ma na GitHubie)
if exist "%PROMPT%" goto lektor
if not exist "pilot\assets\ref_en.wav" (echo Brak nagrania glosu pilot\assets\ref_en.wav ani gotowej probki ref_en_studio.wav - nie ma ich na GitHubie, bo repo jest publiczne. & pause & exit /b 1)
echo [0/3] Probka bez poglosu z ref_en.wav...
"%LEKTOR_ENHANCE%" -I docos\lektor_studio.py probka pilot\assets\ref_en.wav "%PROMPT%" || (pause & exit /b 1)

:lektor
set HF_HUB_OFFLINE=1
echo [1/3] Lektor: 3 podejscia na kwestie, obrobka i wybor...
"%TTS%" -I output\pierwszy-cesarz\lektor_en.py || (echo Nagrywanie przerwane - uruchom jeszcze raz, gotowe podejscia zostaja. & pause & exit /b 1)
echo [2/3] Muzyka i efekty pod dlugosci nagran (output\pierwszy-cesarz\dzwiek_en)...
"%TTS%" -I output\pierwszy-cesarz\efekty.py || (pause & exit /b 1)
echo [3/3] Podglad w Studio (Studio musi dzialac na porcie 8876)...
"%TTS%" -I output\pierwszy-cesarz\studio_pc.py --klipy "%KLIPY_STARE%" || (pause & exit /b 1)
echo Obejrzyj w Studio. Inne podejscie kwestii: output\pierwszy-cesarz\lektor_en\podejscia\wybor.json. Po akceptacji: renderuj_en.bat
pause
