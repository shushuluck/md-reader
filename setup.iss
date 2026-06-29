; MDReader Inno Setup Script

#define MyAppName "MDReader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MDReader"
#define MyAppExeName "MDReader.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MDReader
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer_output
OutputBaseFilename=MDReader_Setup_{#MyAppVersion}
SetupIconFile=icon.ico
UninstallIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional icons:"
Name: "associate_md"; Description: "Associate .md files (double-click to open)"; GroupDescription: "File association:"; Flags: checkedonce

[Files]
Source: "dist\MDReader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\.md\OpenWithProgids"; ValueType: string; ValueName: "MDReader.md"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate_md
Root: HKA; Subkey: "Software\Classes\MDReader.md"; ValueType: string; ValueName: ""; ValueData: "Markdown Document"; Flags: uninsdeletekey; Tasks: associate_md
Root: HKA; Subkey: "Software\Classes\MDReader.md\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"; Tasks: associate_md
Root: HKA; Subkey: "Software\Classes\MDReader.md\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: associate_md
Root: HKA; Subkey: "Software\Classes\.markdown\OpenWithProgids"; ValueType: string; ValueName: "MDReader.md"; ValueData: ""; Flags: uninsdeletevalue; Tasks: associate_md

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch MDReader"; Flags: nowait postinstall skipifsilent
