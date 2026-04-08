@echo off
title Deep-Shield Setup

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Run this file as Administrator!
    echo Right click - Run as Administrator
    pause
    exit /b 1
)

echo Checking Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python not found! Download from python.org
    start https://python.org/downloads
    pause
    exit /b 1
)
python --version

echo.
echo Installing libraries...
python -m pip install --upgrade pip --quiet
python -m pip install scapy scikit-learn seaborn matplotlib pandas joblib PyQt6 numpy --quiet

if %errorLevel% neq 0 (
    echo Install failed! Check internet connection.
    pause
    exit /b 1
)

echo.
echo Checking Npcap...
if exist "C:\Windows\System32\Npcap\wpcap.dll" (
    echo Npcap OK.
) else (
    echo Npcap not found! Opening download page...
    echo Check "WinPcap API-compatible Mode" during install!
    start https://npcap.com/#download
    echo After installing Npcap, run deepshield.bat
    pause
    exit /b 0
)

echo.
echo ================================
echo  Setup complete! Run deepshield.bat
echo ================================
pause
