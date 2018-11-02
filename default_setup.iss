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
#ifndef startMenu_subFolder
	#define startMenu_subFolder "{group}"
#endif

#ifndef icon_startMenu
	#define icon_startMenu
#endif
#ifndef icon_desktop_name
	#define icon_desktop_name appName
#endif

#ifndef canCancel
	#define canCancel "yes"
#endif


[Setup]
AppId = {#uuid}
AppName = {#appName}
AppVersion = {#appVersion}
DefaultDirName = {pf}\{#defaultDir}

#ifdef canCancel
	AllowCancelDuringInstall = {#canCancel}
#endif
#ifdef canRestart
	RestartIfNeededByRun = {#canRestart}
#endif
#ifdef forceLogging
	SetupLogging = {#forceLogging}
#endif

#ifdef startMenuDir
	DefaultGroupName = {#startMenuDir}
#endif
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

#ifdef icon_installer
	SetupIconFile = {#icon_installer}
#endif

[Files]
#ifdef sourceFile
	Source: {#sourceFile}; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
Name: "{#startMenu_subFolder}" ; Filename: "{#pythonPath}"; WorkingDir: "{app}"; Parameters: "{#script}"; IconFilename: "{#icon}"

[Tasks]
#ifdef icon_desktop_state
	Name: {#icon_desktop_name}; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: {#icon_desktop_state}
#endif

