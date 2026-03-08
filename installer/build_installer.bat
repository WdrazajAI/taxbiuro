@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo   Platnik ZUS Exporter - Budowanie instalatora
echo ═══════════════════════════════════════════════════════════════
echo.

:: Sprawdź czy Inno Setup jest zainstalowany
set INNO_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
)

if "%INNO_PATH%"=="" (
    echo [BŁĄD] Inno Setup 6 nie jest zainstalowany!
    echo.
    echo Pobierz i zainstaluj Inno Setup 6 z:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo [✓] Znaleziono Inno Setup: %INNO_PATH%
echo.

:: Przejdź do katalogu głównego projektu
cd /d "%~dp0\.."

:: ═══════════════════════════════════════════════════════════════
:: KROK 1: Utwórz wymagane katalogi
:: ═══════════════════════════════════════════════════════════════
echo [1/5] Tworzenie struktury katalogów...
if not exist "installer\assets" mkdir "installer\assets"
if not exist "installer\output" mkdir "installer\output"
if not exist "redist" mkdir "redist"
echo.

:: ═══════════════════════════════════════════════════════════════
:: KROK 2: Pobierz sterownik ODBC jeśli nie istnieje
:: ═══════════════════════════════════════════════════════════════
echo [2/5] Sprawdzanie sterownika ODBC...
if not exist "redist\msodbcsql.msi" (
    echo      Pobieranie ODBC Driver 17 for SQL Server...
    echo      (To może chwilę potrwać...)

    :: Pobierz oficjalny instalator ODBC od Microsoft
    curl -L -o "redist\msodbcsql.msi" "https://go.microsoft.com/fwlink/?linkid=2249004"

    if errorlevel 1 (
        echo [BŁĄD] Nie udało się pobrać sterownika ODBC!
        echo.
        echo Pobierz ręcznie z: https://go.microsoft.com/fwlink/?linkid=2249004
        echo i umieść jako: redist\msodbcsql.msi
        echo.
        pause
        exit /b 1
    )
    echo      [✓] Sterownik ODBC pobrany
) else (
    echo      [✓] Sterownik ODBC już istnieje
)
echo.

:: ═══════════════════════════════════════════════════════════════
:: KROK 3: Utwórz pliki pomocnicze jeśli nie istnieją
:: ═══════════════════════════════════════════════════════════════
echo [3/5] Sprawdzanie plików pomocniczych...

:: Licencja
if not exist "installer\assets\license.txt" (
    echo Tworzenie license.txt...
    (
        echo PLATNIK ZUS EXPORTER - LICENCJA
        echo ================================
        echo.
        echo Copyright ^(c^) 2024 Wdrazaj.ai
        echo.
        echo Oprogramowanie jest dostarczane "tak jak jest", bez jakiejkolwiek
        echo gwarancji. Autor nie ponosi odpowiedzialności za ewentualne szkody
        echo wynikające z użytkowania tego oprogramowania.
        echo.
        echo Użytkownik przyjmuje do wiadomości, że:
        echo - Aplikacja łączy się z lokalną bazą danych Płatnika
        echo - Dane mogą być wysyłane do zewnętrznego serwisu ^(webhook n8n^)
        echo - Odpowiedzialność za konfigurację i bezpieczeństwo danych
        echo   spoczywa na użytkowniku
        echo.
        echo Klikając "Dalej" akceptujesz powyższe warunki.
    ) > "installer\assets\license.txt"
)

:: Readme
if not exist "installer\assets\readme.txt" (
    echo Tworzenie readme.txt...
    (
        echo PLATNIK ZUS EXPORTER
        echo ====================
        echo.
        echo Aplikacja eksportująca dane o składkach ZUS z programu Płatnik
        echo do systemu automatyzacji n8n.
        echo.
        echo WYMAGANIA:
        echo - Windows 10/11 ^(64-bit^)
        echo - Zainstalowany program Płatnik z bazą SQL Server
        echo - Dostęp sieciowy do bazy danych Płatnika
        echo.
        echo PO INSTALACJI:
        echo 1. Uruchom aplikację
        echo 2. Kliknij ikonę ustawień ^(koło zębate^)
        echo 3. Skonfiguruj połączenie z bazą danych
        echo 4. Wklej URL webhooka n8n
        echo 5. Kliknij "Test połączenia" aby sprawdzić
        echo.
        echo W razie problemów: kontakt@wdrazaj.ai
    ) > "installer\assets\readme.txt"
)

echo      [✓] Pliki pomocnicze gotowe
echo.

:: ═══════════════════════════════════════════════════════════════
:: KROK 4: Zbuduj aplikację .exe
:: ═══════════════════════════════════════════════════════════════
echo [4/5] Budowanie aplikacji...

:: Sprawdź czy Python jest zainstalowany
python --version >nul 2>&1
if errorlevel 1 (
    echo [BŁĄD] Python nie jest zainstalowany!
    pause
    exit /b 1
)

:: Zainstaluj zależności
pip install -r requirements.txt -q

:: Zbuduj .exe
if not exist "dist\PlatnikZUSExporter.exe" (
    echo      Budowanie PlatnikZUSExporter.exe...
    pyinstaller --onefile --windowed --name "PlatnikZUSExporter" --add-data "config.json;." src/main.py -y >nul 2>&1

    if not exist "dist\PlatnikZUSExporter.exe" (
        echo [BŁĄD] Nie udało się zbudować aplikacji!
        pause
        exit /b 1
    )
)

:: Skopiuj config
copy /y config.json dist\ >nul

echo      [✓] Aplikacja zbudowana
echo.

:: ═══════════════════════════════════════════════════════════════
:: KROK 5: Zbuduj instalator
:: ═══════════════════════════════════════════════════════════════
echo [5/5] Budowanie instalatora...

:: Utwórz domyślną ikonę jeśli nie istnieje (placeholder)
if not exist "installer\assets\icon.ico" (
    if exist "assets\icon.ico" (
        copy "assets\icon.ico" "installer\assets\icon.ico" >nul
    ) else (
        echo      [!] Brak ikony - użyj domyślnej
        :: Pomiń ikonę w setup.iss
    )
)

:: Kompiluj instalator
"%INNO_PATH%" "installer\setup.iss"

if errorlevel 1 (
    echo.
    echo [BŁĄD] Kompilacja instalatora nie powiodła się!
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo   SUKCES! Instalator został utworzony!
echo ═══════════════════════════════════════════════════════════════
echo.
echo   Plik: installer\output\PlatnikZUSExporter_Setup_v1.0.0.exe
echo.
echo   Ten plik możesz:
echo   - Wysłać mailem
echo   - Skopiować na pendrive
echo   - Udostępnić przez chmurę (OneDrive, Google Drive)
echo.
echo   Odbiorca uruchamia instalator i wszystko działa automatycznie!
echo.
pause
