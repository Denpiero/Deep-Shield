@echo off
chcp 65001 >nul
title Deep-Shield

:: YÖNETİCİ KONTROLÜ (scapy için zorunlu)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Deep-Shield ag dinlemesi icin yonetici yetkisi gerektirir.
    echo  [!] Lutfen bu dosyaya sag tiklayin ve
    echo  [!] "Yonetici olarak calistir" secin!
    echo.
    pause
    exit /b 1
)

:: KURULUM YAPILDI MI KONTROL ET
python -c "import scapy, sklearn, PyQt6" >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Kutuphaneler eksik! Once kurulum.bat calistirin.
    pause
    exit /b 1
)

:: PROGRAMI BAŞLAT
echo  [*] Deep-Shield baslatiliyor...
python src\arayuz.py

if %errorLevel% neq 0 (
    echo.
    echo  [HATA] Program baslatılamadı.
    echo  Once kurulum.bat calistirdiginizdan emin olun.
    pause
)
