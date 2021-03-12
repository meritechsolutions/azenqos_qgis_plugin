@echo off
echo === AZENQOS log file analysis QGIS plugin installer ===
echo - Please make sure QGIS is closed first.
echo - Any existing Azenqos plugins would get deleted and replaced

echo == Finding local QGIS installation folder...
For /F "Skip=1 Tokens=2*" %%A In (
    'reg query "HKLM\SOFTWARE\QGIS 3.10" -v InstallPath 2^>Nul'
) Do Set "EP10=%%~B"

if defined EP10 (
    Echo Found QGIS InstallPath: %EP10%
    echo == Preparing QGIS10 cmd env...
    call "%EP10%\bin\o4w_env.bat" || (echo INSTALL FAILED && pause && exit 1)
    call "py3_env" || (echo INSTALL FAILED && pause && exit 1)
    echo == Installing required python packages into QGIS's python env...
    python3 -m pip install -r requirements.txt || (echo INSTALL FAILED && pause && exit 1)
)

For /F "Skip=1 Tokens=2*" %%A In (
    'reg query "HKLM\SOFTWARE\QGIS 3.16" -v InstallPath 2^>Nul'
) Do Set "EP16=%%~B"

if defined EP16 (
    Echo Found QGIS InstallPath: %EP16%
    echo == Preparing QGIS16 cmd env...
    call "%EP16%\bin\o4w_env.bat" || (echo INSTALL FAILED && pause && exit 1)
    call "py3_env" || (echo INSTALL FAILED && pause && exit 1)
    echo == Installing required python packages into QGIS's python env...
    python3 -m pip install -r requirements.txt || (echo INSTALL FAILED && pause && exit 1)
)

if not defined EP16 (
    if not defined EP10 (
        echo NO QGIS FOUND && pause && exit 1
    )
) 

echo == Removing any existing plugin folders...
rmdir /q /s "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\Azenqos"

echo == Copying new plugin from this folder...
xcopy /E /I Azenqos "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\Azenqos" || (echo INSTALL FAILED && pause && exit 1)

echo === INSTAL SUCCESS - you can start QGIS now
echo "If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin"
pause
