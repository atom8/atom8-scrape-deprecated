cd /D "%~dp0"
call venv\Scripts\activate.bat
python run_gui.py
deactivate
