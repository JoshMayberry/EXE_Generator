#ifndef uuid
	#define uuid 982970ca-28cd-40c2-b56d-d63439ce0381
#endif

#ifndef appName
	#define appName "MyApp"
#endif

#ifndef appVersion
	#define appVersion "unknown"
#endif

#ifndef defaultDir
	#define defaultDir appName
#endif

#ifndef icon_installer
	#define icon_installer
#endif

#ifndef icon_startMenu
	#define icon_startMenu
#endif

#ifndef icon_desktop_name
	#define icon_desktop_name appName
#endif

#ifndef canCancel
	#define canCancel yes
#endif


[Setup]
AppId = {#uuid}
AppName = {#appName}
AppVersion = {#appVersion}
DefaultDirName = {pf}\{#defaultDir}

AllowCancelDuringInstall {#canCancel}

SetupIconFile = {#icon_installer}


[Files]
#ifdef sourceFile
	Source: {#sourceFile}; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{group}\{#startMenu_Folder}" ; Filename: "{#pythonPath}"; WorkingDir: "{app}"; Parameters: "{#script}"; IconFilename: "{#icon}"

[Tasks]
#ifdef icon_desktop_state
	Name: {#icon_desktop_name}; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: {#icon_desktop_state}
#endif

