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

#ifndef canCancel
	#define canCancel "yes"
#endif

[Setup]
AppId = {#uuid}
AppName = {#appName}
AppVersion = {#appVersion}
DefaultDirName = {pf}\{#defaultDir}
DefaultGroupName = {#startMenuDir}
SetupIconFile = {#icon_installer}

#ifdef canCancel
	AllowCancelDuringInstall = {#canCancel}
#endif
#ifdef canRestart
	RestartIfNeededByRun = {#canRestart}
#endif
;#ifdef forceLogging
;	SetupLogging = {#forceLogging}
;#endif

#ifdef outputDir
	OutputDir = {#outputDir}
#endif
#ifdef manifest
	OutputManifestFile = {#manifest}
#endif

#ifdef publisher
	AppPublisher = {#publisher}
#endif
#ifdef publisherWebsite
	AppPublisherURL = {#publisherWebsite}
#endif
#ifdef supportWebsite
	AppSupportURL = {#supportWebsite}
#endif
#ifdef supportPhone
	AppSupportPhone = {#supportPhone}
#endif
#ifdef updateWebsite
	AppUpdatesURL = {#updateWebsite}
#endif
#ifdef readmeWebsite
	AppReadmeFile = {#readmeWebsite}
#endif
#ifdef preInfoPage
	InfoBeforeFile = {#preInfoPage}
#endif
#ifdef postInfoPage
	InfoAfterFile = {#postInfoPage}
#endif

#ifdef update_fileAssociations
	ChangesAssociations = {#update_fileAssociations}
#endif
#ifdef update_environment
	ChangesEnvironment = {#update_environment}
#endif
#ifdef closeApps
	CloseApplications = {#closeApps}
#endif
#ifdef restartApps
	RestartApplications = {#restartApps}
#endif
#ifdef regkey_uninstall
	CreateUninstallRegKey = {#regkey_uninstall}
#endif
#ifdef dirExistsWarning
	DirExistsWarning = {#dirExistsWarning}
#endif
#ifdef skip_startupMessage
	DisableStartupPrompt = {#skip_startupMessage}
#endif
#ifdef skip_welcomePage
	DisableWelcomePage = {#skip_welcomePage}
#endif
#ifdef windows_minVersion
	MinVersion = {#windows_minVersion}
#endif
#ifdef windows_maxVersion
	OnlyBelowVersion = {#windows_maxVersion}
#endif

[Types]
Name: "full"; Description: "Full installation"
Name: "compact"; Description: "Compact installation"
Name: "custom"; Description: "Custom installation"; Flags: iscustom

[Components]
Name: "main"; Description: "Main Files"; Types: full compact custom; Flags: fixed

[Tasks]
Name: desktopicon; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Components: main
Name: desktopicon\common; Description: "For all users"; GroupDescription: "{cm:AdditionalIcons}:"; Components: main; Flags: exclusive
Name: desktopicon\user; Description: "For the current user only"; GroupDescription: "{cm:AdditionalIcons}:"; Components: main; Flags: exclusive unchecked
; Name: quicklaunchicon; Description: {cm:CreateQuickLaunchIcon}; GroupDescription: "{cm:AdditionalIcons}:"; Components: main; Flags: unchecked
; Name: associate; Description: {cm:AssocFileExtension}; GroupDescription: "Other tasks:"; Flags: unchecked
Name: startmenu; Description: "Create Start Menu icon"; GroupDescription: "{cm:AdditionalIcons}"; Components: main

[Files]
Source: {#icon}; DestDir: "{app}"; Components: main

#ifdef shortcutDesktop_script
	[Files]
	Source: {#shortcutDesktop_icon_source}; DestDir: "{app}"; Components: main; Tasks: desktopicon
	Source: {#shortcutDesktop_source}; DestDir: {#shortcutDesktop_destination}; Components: main; Tasks: desktopicon

	[Icons]
	#if shortcutDesktop_isPython
		Name: "{userdesktop}\{#shortcutDesktop_name}"; Filename: "{#pythonPath}"; WorkingDir: "{#shortcutDesktop_workingDir}"; Parameters: " ""{#shortcutDesktop_script}"" {#shortcutDesktop_params} "; IconFilename: "{#shortcutDesktop_icon}"; Tasks: desktopicon\user
		Name: "{commondesktop}\{#shortcutDesktop_name}"; Filename: "{#pythonPath}"; WorkingDir: "{#shortcutDesktop_workingDir}"; Parameters: " ""{#shortcutDesktop_script}"" {#shortcutDesktop_params} "; IconFilename: "{#shortcutDesktop_icon}"; Tasks: desktopicon\common
	#else
		Name: "{userdesktop}\{#shortcutDesktop_name}"; Filename:  "{#shortcutDesktop_script}"; WorkingDir: "{#shortcutDesktop_workingDir}"; Parameters: "{#shortcutDesktop_params} "; IconFilename: "{#shortcutDesktop_icon}"; Tasks: desktopicon\user
		Name: "{commondesktop}\{#shortcutDesktop_name}"; Filename:  "{#shortcutDesktop_script}"; WorkingDir: "{#shortcutDesktop_workingDir}"; Parameters: "{#shortcutDesktop_params} "; IconFilename: "{#shortcutDesktop_icon}"; Tasks: desktopicon\common
	#endif
#endif

#ifdef shortcutStartMenu_script
	[Files]
	Source: {#shortcutStartMenu_icon_source}; DestDir: "{app}"; Components: main; Tasks: startmenu
	Source: {#shortcutStartMenu_source}; DestDir: {#shortcutStartMenu_destination}; Components: main; Tasks: startmenu

	[Icons]
	#if shortcutStartMenu_isPython
		Name: "{group}\{#shortcutStartMenu_name}"; Filename: "{#pythonPath}"; WorkingDir: "{#shortcutStartMenu_workingDir}"; Parameters: " ""{#shortcutStartMenu_script}"" {#shortcutStartMenu_params} "; IconFilename: "{#shortcutStartMenu_icon}"; Tasks: startmenu
	#else
		Name: "{group}\{#shortcutDesktop_name}"; Filename:  "{#shortcutDesktop_script}"; WorkingDir: "{#shortcutDesktop_workingDir}"; Parameters: "{#shortcutDesktop_params} "; IconFilename: "{#shortcutDesktop_icon}"; Tasks: startmenu
	#endif
#endif
