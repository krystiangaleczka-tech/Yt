@echo off
rem Pierwszy cesarz - krok 1: lektor (klon głosu autora, Chatterbox Multilingual na karcie NVIDIA) do output\pierwszy-cesarz\lektor.
rem Uruchamiaj z klonu repozytorium. Gotowe kwestie są pomijane: przerwane nagrywanie wznawia się od miejsca przerwania.
chcp 65001 >nul
cd /d "%~dp0..\..\.."
where ffmpeg >nul 2>nul || (echo Brak ffmpeg w PATH. Zainstaluj: winget install Gyan.FFmpeg i otwórz nowe okno. & pause & exit /b 1)
if not exist "pilot\assets\ref_clean.wav" (echo Brak próbki głosu. Skopiuj ref_clean.wav do folderu pilot\assets\ w repozytorium - nie ma jej na GitHubie, bo repo jest publiczne. & pause & exit /b 1)
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
"%TTS%" output\pierwszy-cesarz\lektor.py
echo.
echo Lektor gotowy. Teraz uruchom renderuj.bat.
pause
