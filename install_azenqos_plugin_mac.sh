#!/bin/bash

exit_if_failed() {
    if [ $? -ne 0 ]; then
	echo "ABORT: Previous step failed"
	exit 1
    fi
}

echo "=== AZENQOS log file analysis QGIS plugin installer ==="
echo "Please make sure QGIS is closed first."
echo "Any existing Azenqos plugins would get deleted and replaced"
echo "== Finding local QGIS installation folder..."

echo "== Removing any existing plugin folders..."
rm -rf /Applications/QGIS3.10.app/Contents/PlugIns/Azenqos

echo == Copying new plugin from this folder...
cp -a `pwd`/Azenqos /Applications/QGIS3.10.app/Contents/PlugIns/Azenqos
exit_if_failed

echo "== Installing required python packages into QGIS's python env..."
/Applications/QGIS3.10.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 -m pip install --prefix /Applications/QGIS3.10.app/Contents/Frameworks/Python.framework/Versions/Current -r requirements.txt
exit_if_failed

echo
echo === INSTAL SUCCESS - you can start QGIS now
echo "If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin"

