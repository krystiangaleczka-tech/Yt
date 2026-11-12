@echo off
rem Pierwszy cesarz - krok 1: lektor (klon głosu autora, Chatterbox Multilingual na karcie NVIDIA) do output\pierwszy-cesarz\lektor.
rem Sposób z Podręcznika pracowni - Lektor: próbka bez pogłosu, 3 podejścia na kwestię, suche i z odbudowanym pasmem
rem (resemble-enhance), wybór podejścia z oddechami na przecinkach.
rem Uruchamiaj z klonu repozytorium. Gotowe podejścia są pomijane: przerwane nagrywanie wznawia się od miejsca przerwania.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
where ffmpeg >nul 2>nul || (echo Brak ffmpeg w PATH. Zainstaluj: winget install Gyan.FFmpeg i otwórz nowe okno. & pause & exit /b 1)
if not exist "pilot\assets\ref_studio.wav" (echo Brak próbki głosu bez pogłosu. Skopiuj ref_studio.wav do folderu pilot\assets\ w repozytorium - nie ma jej na GitHubie, bo repo jest publiczne. & pause & exit /b 1)

rem środowisko odbudowy pasma i suchego brzmienia (resemble-enhance) - osobne, inne wersje bibliotek niż Chatterbox
set "LEKTOR_ENHANCE=%CD%\.venv-enhance\Scripts\python.exe"
if exist "%LEKTOR_ENHANCE%" goto tts
echo Tworzę środowisko resemble-enhance (jednorazowo, kilka GB: PyTorch z CUDA)...
py -3.11 -m venv .venv-enhance || (echo Potrzebny Python 3.11: winget install Python.Python.3.11 & pause & exit /b 1)
"%LEKTOR_ENHANCE%" -m pip install --upgrade pip
"%LEKTOR_ENHANCE%" -m pip install torch==2.4.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu124
"%LEKTOR_ENHANCE%" -m pip install resemble-enhance==0.0.1 --no-deps
"%LEKTOR_ENHANCE%" -m pip install -r requirements-enhance.txt

:tts
set "TTS=%USERPROFILE%\.zombie-tts\venv\Scripts\python.exe"
if exist "%TTS%" goto nagraj
set "TTS=%CD%\.venv-tts\Scripts\python.exe"
if exist "%TTS%" goto nagraj
echo Tworzę środowisko lektora (jednorazowo, kilka GB: PyTorch z CUDA i Chatterbox)...
py -3.11 -m venv .venv-tts || (echo Potrzebny Python 3.11: winget install Python.Python.3.11 & pause & exit /b 1)
"%TTS%" -m pip install --upgrade pip
"%TTS%" -m pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
"%TTS%" -m pip install chatterbox-tts==0.1.7 soundfile
:nagraj
"%TTS%" -c "import torch; print('karta:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'BRAK - nagrywanie na procesorze bedzie bardzo wolne')"
"%TTS%" output\pierwszy-cesarz\lektor.py || (echo Nagrywanie przerwane - uruchom jeszcze raz, gotowe podejścia zostają. & pause & exit /b 1)
echo.
echo Lektor gotowy. Teraz uruchom renderuj.bat.
pause
