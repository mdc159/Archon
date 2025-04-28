@echo off
cd /d X:\GitHub\Archon
call .venv\Scripts\activate.bat
python run_docker.py
streamlit run streamlit_ui.py
pause 