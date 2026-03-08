; Platnik ZUS Exporter - Inno Setup Script
; Automatyczna instalacja aplikacji + sterownika ODBC

#define MyAppName "Platnik ZUS Exporter"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Wdrazaj.ai"
#define MyAppURL "https://wdrazaj.ai"
#define MyAppExeName "PlatnikZUSExporter.exe"

[Setup]
; Podstawowe ustawienia
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Lokalizacja instalacji
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Wyjściowy plik instalatora
OutputDir=output
OutputBaseFilename=PlatnikZUSExporter_Setup_v{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes

; Wymagania Windows
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Wygląd
WizardStyle=modern

; Uprawnienia
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Licencja i informacje
LicenseFile=assets\license.txt
InfoBeforeFile=assets\readme.txt

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"

[Messages]
polish.BeveledLabel=Platnik ZUS Exporter

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Główna aplikacja
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Konfiguracja
Source: "..\config.json"; DestDir: "{app}"; Flags: ignoreversion onlyifdoesntexist

; Sterownik ODBC (pakowany z instalatorem)
Source: "redist\msodbcsql.msi"; DestDir: "{tmp}"; Flags: ignoreversion deleteafterinstall; Check: not IsODBCDriverInstalled

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Instalacja ODBC jeśli nie jest zainstalowany
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\msodbcsql.msi"" /quiet /norestart IACCEPTMSODBCSQLLICENSETERMS=YES"; StatusMsg: "Instalowanie sterownika ODBC dla SQL Server..."; Flags: runhidden waituntilterminated; Check: not IsODBCDriverInstalled

; Uruchom aplikację po instalacji
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Sprawdza czy sterownik ODBC jest już zainstalowany
function IsODBCDriverInstalled: Boolean;
var
  DriverPath: String;
begin
  Result := False;

  // Sprawdź ODBC Driver 17
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 17 for SQL Server',
    'Driver', DriverPath) then
  begin
    Result := True;
    Exit;
  end;

  // Sprawdź ODBC Driver 18
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 18 for SQL Server',
    'Driver', DriverPath) then
  begin
    Result := True;
    Exit;
  end;

  // Sprawdź starsze wersje (13, 11)
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\ODBC\ODBCINST.INI\ODBC Driver 13 for SQL Server',
    'Driver', DriverPath) then
  begin
    Result := True;
    Exit;
  end;
end;

// Wyświetl informację o ODBC przed instalacją
function InitializeSetup: Boolean;
begin
  Result := True;

  if not IsODBCDriverInstalled then
  begin
    if MsgBox('Sterownik ODBC dla SQL Server nie jest zainstalowany.' + #13#10 + #13#10 +
              'Instalator automatycznie zainstaluje wymagany sterownik.' + #13#10 +
              'Wymaga to uprawnień administratora.' + #13#10 + #13#10 +
              'Czy chcesz kontynuować?',
              mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end;
  end;
end;

// Podsumowanie po instalacji
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not IsODBCDriverInstalled then
    begin
      MsgBox('UWAGA: Nie udało się zainstalować sterownika ODBC.' + #13#10 + #13#10 +
             'Pobierz go ręcznie z:' + #13#10 +
             'https://go.microsoft.com/fwlink/?linkid=2249004' + #13#10 + #13#10 +
             'Aplikacja nie będzie działać bez sterownika ODBC.',
             mbError, MB_OK);
    end;
  end;
end;
