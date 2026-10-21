@echo off
chcp 65001 >nul
title Görsel Üretimi

cd /d "%~dp0"

echo Görsel üretimi başlatılıyor...
echo.

:: Python kontrolü
set "PY_CMD="
where py >nul 2>nul
if not errorlevel 1 (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py -3"
)

if "%PY_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 set "PY_CMD=python"
)

if "%PY_CMD%"=="" (
    echo HATA: Python bulunamadı.
    echo Python'u kurup tekrar deneyin: https://www.python.org/downloads/
    echo Kurulum sırasında "Add Python to PATH" seçeneğini işaretlemeyi unutmayın.
    echo.
    pause
    exit /b 1
)

:: Gerekli kütüphaneleri kontrol et ve gerekirse otomatik yükle
%PY_CMD% -c "import requests, dotenv" >nul 2>nul
if errorlevel 1 (
    echo Gerekli Python paketleri eksik, yukleniyor: requests, python-dotenv...
    %PY_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo HATA: Kütüphaneler yüklenemedi. Lütfen internet bağlantınızı kontrol edin.
        pause
        exit /b 1
    )
    echo Paketler başarıyla yüklendi.
    echo.
)

:: Scripti çalıştır
%PY_CMD% -u generate_all.py
set "RESULT=%errorlevel%"

echo.
if not "%RESULT%"=="0" (
    echo İşlem bir hatayla sona erdi. Yukarıdaki hata mesajını kontrol edin.
) else (
    echo İşlem tamamlandı. Sonuçlar "cikti" klasörüne kaydedildi.
)
echo.
pause
exit /b %RESULT%
