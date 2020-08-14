@echo off
echo === AZENQOS log file analysis QGIS plugin installer ===
echo - Please make sure QGIS is closed first.
echo - Any existing Azenqos plugins would get deleted and replaced

echo == Finding local QGIS installation folder...
For /F "Skip=1 Tokens=2*" %%A In (
    'reg query "HKLM\SOFTWARE\QGIS 3.10" -v InstallPath 2^>Nul'
) Do Set "EP=%%~B"
Echo Found QGIS InstallPath: %EP%

echo == Preparing QGIS cmd env...
call "%EP%\bin\o4w_env.bat" || (echo INSTALL FAILED && pause && exit 1)
call "py3_env" || (echo INSTALL FAILED && pause && exit 1)

echo == Installing required python packages into QGIS's python env...
python3 -m pip install -r requirements.txt || (echo INSTALL FAILED && pause && exit 1)

echo == Removing any existing plugin folders...
rmdir /q /s "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\Azenqos"

echo == Copying new plugin from this folder...
xcopy /E /I Azenqos "%appdata%\QGIS\QGIS3\profiles\default\python\plugins\Azenqos" || (echo INSTALL FAILED && pause && exit 1)

echo === INSTAL SUCCESS - you can start QGIS now
echo "If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin"
pause
