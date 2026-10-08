@echo off
title Trading Journal Pro - Setup
echo.
echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Setup complete.
echo Run the journal with:
echo streamlit run app.py
echo.
pause
