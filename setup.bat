@echo off
cd /d "%~dp0"
py -3 -m venv venv
if errorlevel 1 goto err
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Setup finished. Open .env in Notepad and paste your API key (optional), then run run.bat
pause
goto :eof
:err
echo Python not found. Install Python 3.10+ from python.org and tick "Add python.exe to PATH".
pause
