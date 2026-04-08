@echo off
chcp 65001 >nul
title Deep-Shield Kurulum

echo.
echo  ========================================
echo   DEEP-SHIELD - Kurulum Basliyor
echo  ========================================
echo.

:: YÖNETİCİ KONTROLÜ
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Lutfen bu dosyaya sag tiklayin ve
    echo  [!] "Yonetici olarak calistir" secin!
    echo.
    pause
    exit /b 1
)

:: PYTHON KONTROLÜ
echo  [1/3] Python kontrol ediliyor...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo  [HATA] Python bulunamadi!
    echo  https://python.org adresinden Python 3.10+ yukleyin.
    start https://python.org/downloads
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo  [OK] %%i
echo.

:: KÜTÜPHANELERİ YÜKLE
echo  [2/3] Kutuphaneler yukleniyor...
echo  (1-3 dakika surebilir, lutfen bekleyin)
echo.
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %errorLevel% neq 0 (
    echo  [HATA] Kutuphaneler yuklenemedi!
    echo  Internet baglantinizi kontrol edin.
    pause
    exit /b 1
)
echo  [OK] Kutuphaneler yuklendi!
echo.

:: NPCAP KONTROLÜ
echo  [3/3] Npcap kontrol ediliyor...
if exist "C:\Windows\System32\Npcap\wpcap.dll" (
    echo  [OK] Npcap zaten yuklu.
) else if exist "C:\Windows\System32\wpcap.dll" (
    echo  [OK] WinPcap bulundu.
) else (
    echo  [!] Npcap yuklu degil - ag dinlemesi icin zorunludur!
    echo  [!] Tarayicinizda Npcap indirme sayfasi aciliyor...
    start https://npcap.com/#download
    echo.
    echo  Npcap'i kurun, sonra deepshield.bat ile programi baslatin.
    pause
    exit /b 0
)

echo.
echo  ========================================
echo   KURULUM TAMAMLANDI!
echo   Simdi deepshield.bat calistirin.
echo  ========================================
echo.
pause
