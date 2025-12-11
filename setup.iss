[Setup]
; Basic Application Information
AppName=RedLight DL
AppVersion=2.1.0
AppPublisher=RedLight Team
AppExeName=RedLightGUI.exe
DefaultDirName={autopf}\RedLightDL
DefaultGroupName=RedLight DL
OutputBaseFilename=RedLightSetup
OutputDir=Output
Compression=lzma2/max
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
; Dark Mode Support for Installer
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; The Main Executable
Source: "gui\host\bin\Release\net8.0-windows\publish\RedLightGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
; The Helper DLLs and Configs from .NET Publish
Source: "gui\host\bin\Release\net8.0-windows\publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; The Python Backend (Bundled) - We assume it's copied to the publish folder or we source it from dist
; Let's source it from the dist folder and put it in RedLightServer subdir
Source: "dist\RedLightServer\*"; DestDir: "{app}\RedLightServer"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\RedLight DL"; Filename: "{app}\RedLightGUI.exe"
Name: "{autodesktop}\RedLight DL"; Filename: "{app}\RedLightGUI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RedLightGUI.exe"; Description: "{cm:LaunchProgram,RedLight DL}"; Flags: nowait postinstall skipifsilent
