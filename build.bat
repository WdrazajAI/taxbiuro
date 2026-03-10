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

echo [1/2] Instalowanie zaleznosci...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Blad podczas instalacji zaleznosci
    pause
    exit /b 1
)

echo.
echo [2/2] Budowanie pliku .exe...
REM Config is stored in %%APPDATA%%\PlatnikZUSExporter\ (not alongside exe)
REM This is the standard Windows way - Program Files is read-only
pyinstaller --onefile ^
    --windowed ^
    --name "PlatnikZUSExporter" ^
    src/main.py

if errorlevel 1 (
    echo [ERROR] Blad podczas budowania .exe
    pause
    exit /b 1
)

echo.
echo =========================================
echo   BUILD ZAKONCZONY POMYSLNIE!
echo =========================================
echo.
echo Plik .exe znajduje sie w folderze: dist\PlatnikZUSExporter.exe
echo.
echo INFORMACJA:
echo - Konfiguracja jest zapisywana w: %%APPDATA%%\PlatnikZUSExporter\config.json
echo - Mozesz uruchomic exe z dowolnego miejsca (np. z pulpitu)
echo - Aby stworzyc instalator: uruchom installer\build_installer.bat
echo.
pause
