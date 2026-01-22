; Inno Setup Script para Calcpad Fork WPF
; Genera un instalador setup.exe con todo incluido

#define MyAppName "Calcpad Fork"
#define MyAppVersion "1.0.2"
#define MyAppPublisher "Calcpad Fork Project"
#define MyAppURL "https://github.com/GiorgioBurbanelli89/calcpad_fork"
#define MyAppExeName "Calcpad.exe"

[Setup]
; Información de la aplicación
AppId={{A7C8E3F2-5B4D-4C6E-8F1A-2D9B7E4C6A5F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\CalcpadFork
DefaultGroupName=Calcpad Fork
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=.\Installer
OutputBaseFilename=CalcpadFork-Setup-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
;SetupIconFile={#SourcePath}\Calcpad.Wpf\resources\calcpad.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
Name: "fileassoc"; Description: "Asociar archivos .cpd con {#MyAppName}"; GroupDescription: "Asociaciones de archivos:"

[Files]
; Ejecutable principal de Calcpad.Wpf y todas sus dependencias
Source: "Calcpad.Wpf\bin\Release\net10.0-windows\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

; Configuración de lenguajes externos actualizada (CSS, HTML, TypeScript, etc.)
Source: "Calcpad.Common\MultLangCode\MultLangConfig.json"; DestDir: "{app}"; Flags: ignoreversion

; Ejemplos de HTML + CSS + TypeScript
Source: "Examples\Practica_Simple_HTML_CSS_TS.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Examples\Practica_HTML_CSS_TS_Combinado.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Examples\Practica_Avanzada_Reactive_HTML_CSS_TS.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist

; Ejemplos corregidos con CSS en HTML (sin @{css} separado)
Source: "Examples\Practica_Simple_HTML_TS_CORREGIDA.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Examples\Practica_Avanzada_Reactive_CORREGIDA.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist

; Ejemplo de generación y guardado de archivos web
Source: "Examples\Demo_Generar_y_Guardar_Archivos.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist

; Ejemplos de TypeScript
Source: "Examples\Test_TypeScript_@ts.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Examples\TypeScript_en_Calcpad.cpd"; DestDir: "{app}\Examples"; Flags: ignoreversion skipifsourcedoesntexist

; Otros ejemplos existentes
Source: "Examples\*"; DestDir: "{app}\Examples"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist

; Documentación general
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme skipifsourcedoesntexist
Source: "CHANGELOG.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; Documentación de HTML + CSS + TypeScript
Source: "HTML_CSS_TYPESCRIPT_LISTO.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion
Source: "COMO_FUNCIONA_AWATIF_UI.md"; DestDir: "{app}\Docs"; Flags: ignoreversion
Source: "CHEAT_SHEET_HTML_CSS_TS.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion
Source: "RESUMEN_SESION_HTML_CSS_TS_AWATIF.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "INDICE_ARCHIVOS_CREADOS.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist

; Documentación de TypeScript
Source: "TYPESCRIPT_LISTO.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "TYPESCRIPT_@TS_CONFIGURADO.md"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "RESUMEN_TYPESCRIPT_@TS.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist

; Documentación de fixes críticos v1.0.1
Source: "AUDITORIA_COMPLETA_MATHEDITOR.md"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "FIXES_CRITICOS_MEMORY_LEAKS_APLICADOS.md"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "RESUMEN_FINAL_TODOS_LOS_FIXES.md"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "TODOS_LOS_FIXES_APLICADOS.md"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist

; Documentación del sistema de archivos separados y guardado
Source: "NUEVO_SISTEMA_ARCHIVOS_SEPARADOS.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "PROBLEMA_CSS_SOLUCION.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "COMO_GUARDAR_ARCHIVOS_WEB.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "RESUMEN_GUARDAR_ARCHIVOS_WEB.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist
Source: "REFERENCIA_RAPIDA_GUARDAR_WEB.txt"; DestDir: "{app}\Docs"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Registry]
; Asociación de archivos .cpd
Root: HKA; Subkey: "Software\Classes\.cpd"; ValueType: string; ValueName: ""; ValueData: "CalcpadFile"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\CalcpadFile"; ValueType: string; ValueName: ""; ValueData: "Calcpad File"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\CalcpadFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: fileassoc
Root: HKA; Subkey: "Software\Classes\CalcpadFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: fileassoc

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
  DotnetPath: String;
begin
  Result := True;

  // Verificar si dotnet.exe existe
  DotnetPath := ExpandConstant('{pf}\dotnet\dotnet.exe');
  if not FileExists(DotnetPath) then
  begin
    DotnetPath := ExpandConstant('{pf64}\dotnet\dotnet.exe');
  end;

  // Si dotnet existe, asumir que .NET 10 está instalado
  if not FileExists(DotnetPath) then
  begin
    if MsgBox('Este programa requiere .NET 10 Desktop Runtime.' + #13#10 +
              '¿Desea abrir la página de descarga de .NET 10?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://dotnet.microsoft.com/download/dotnet/10.0', '', '', SW_SHOW, ewNoWait, ErrorCode);
    end;
    Result := False;
  end;
end;
