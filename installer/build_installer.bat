@echo off
echo ===================================
echo   Platnik ZUS Exporter - Installer
echo ===================================
echo.

:: Check Inno Setup
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%INNO_PATH%"=="" (
    echo [ERROR] Inno Setup 6 not installed!
    echo Download from: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

echo [OK] Found Inno Setup
echo.

:: Go to project root
cd /d "%~dp0\.."

:: Create directories
echo [1/5] Creating directories...
if not exist "installer\output" mkdir "installer\output"
if not exist "installer\redist" mkdir "installer\redist"
echo.

:: Download ODBC driver
echo [2/5] Checking ODBC driver...
if not exist "installer\redist\msodbcsql.msi" (
    echo      Downloading ODBC Driver 17...
    curl -L -o "installer\redist\msodbcsql.msi" "https://go.microsoft.com/fwlink/?linkid=2249004"
    if errorlevel 1 (
        echo [ERROR] Failed to download ODBC driver
        echo Download manually: https://go.microsoft.com/fwlink/?linkid=2249004
        pause
        exit /b 1
    )
    echo      [OK] ODBC driver downloaded
) else (
    echo      [OK] ODBC driver exists
)
echo.

:: Check Python
echo [3/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not installed!
    pause
    exit /b 1
)
echo      [OK] Python found
echo.

:: Build exe
echo [4/5] Building application...
pip install -r requirements.txt -q 2>nul
pip install pyinstaller -q 2>nul

if not exist "dist\PlatnikZUSExporter.exe" (
    echo      Running PyInstaller...
    python -m PyInstaller --onefile --windowed --name "PlatnikZUSExporter" src/main.py -y
    if errorlevel 1 (
        echo [ERROR] PyInstaller failed!
        pause
        exit /b 1
    )
) else (
    echo      [OK] EXE already exists
)
echo.

:: Build installer
echo [5/5] Building installer...
"%INNO_PATH%" "installer\setup.iss"
if errorlevel 1 (
    echo [ERROR] Inno Setup compilation failed!
    pause
    exit /b 1
)

echo.
echo ===================================
echo   SUCCESS!
echo ===================================
echo.
echo   Output: installer\output\PlatnikZUSExporter_Setup_v1.0.0.exe
echo.
pause
