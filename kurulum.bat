@echo off
title Deep-Shield Kurulum Yardimcisi
color 0b

echo ======================================================
echo       DEEP-SHIELD KUTUPHANE KURULUMU BASLIYOR
echo ======================================================
echo.

:: Python yuklu mu kontrol et
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0c
    echo [HATA] Python bulunamadi! Lutfen Python yukleyin ve 'Add to PATH' secenegini isaretleyin.
    pause
    exit
)

echo [+] Python bulundu. Kutuphaneler yukleniyor...
echo.

:: Pip guncelleme
python -m pip install --upgrade pip

:: Kutuphaneleri yukle
:: gereksinimler.txt varsa oradan oku, yoksa manuel yukle
if exist gereksinimler.txt (
    echo [+] gereksinimler.txt bulundu, yukleniyor...
    pip install -r gereksinimler.txt
) else (
    echo [!] gereksinimler.txt bulunamadi, manuel kurulum yapiliyor...
    pip install scapy pandas numpy scikit-learn joblib matplotlib seaborn PyQt6
)

echo.
echo ======================================================
echo       KURULUM TAMAMLANDI!
echo ======================================================
echo.
echo Not: Windows kullaniyorsaniz Npcap yuklemeyi unutmayin.
echo Simdi ana programi baslatabilirsiniz.
echo.
pause