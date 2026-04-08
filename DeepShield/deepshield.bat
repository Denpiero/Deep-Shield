cd /d "%~dp0"
@echo off
title Deep-Shield

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Run this file as Administrator!
    echo Right click - Run as Administrator
    pause
    exit /b 1
)

python -c "import scapy, sklearn, PyQt6" >nul 2>&1
if %errorLevel% neq 0 (
    echo Libraries missing! Run kurulum.bat first.
    pause
    exit /b 1
)

echo Starting Deep-Shield...
python "..\src\arayuz.py"

if %errorLevel% neq 0 (
    echo Program failed to start. Run kurulum.bat first.
    pause
)
