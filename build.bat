@echo off
echo =========================================
echo   Platnik ZUS Exporter - Build Script
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nie jest zainstalowany!
    echo Pobierz Python z https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Instalowanie zaleznosci...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Blad podczas instalacji zaleznosci
    pause
    exit /b 1
)

echo.
echo [2/3] Budowanie pliku .exe...
pyinstaller --onefile ^
    --windowed ^
    --name "PlatnikZUSExporter" ^
    --add-data "config.json;." ^
    --add-data "klienci_email.csv;." ^
    src/main.py

if errorlevel 1 (
    echo [ERROR] Blad podczas budowania .exe
    pause
    exit /b 1
)

echo.
echo [3/3] Kopiowanie plikow konfiguracyjnych...
copy config.json dist\
copy klienci_email.csv dist\

echo.
echo =========================================
echo   BUILD ZAKONCZONY POMYSLNIE!
echo =========================================
echo.
echo Plik .exe znajduje sie w folderze: dist\
echo.
echo Aby uruchomic, skopiuj caly folder dist\
echo na komputer z baza Platnika.
echo.
echo Pliki w folderze dist\:
dir dist\ /b
echo.
pause
