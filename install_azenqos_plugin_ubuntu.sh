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

echo "== Installing required python packages into QGIS's python env..."
python3 -m pip install -r requirements.txt
exit_if_failed

echo == Removing any existing plugin folders...
rm -rf ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Azenqos

echo == Copying new plugin from this folder...
ln -s `pwd`/Azenqos ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Azenqos
exit_if_failed
echo
echo === INSTAL SUCCESS - you can start QGIS now
echo "If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin"

