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

echo "note: pyqt5 pip must not be installed as it should be installed by qgis already - do not install in pip again as it will conflict and qgis launch python would fail"
echo "== Installing required python packages into local python3 env..."
sudo python3 -m pip install -r requirements.txt
exit_if_failed

mkdir -p $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/

echo == Removing any existing plugin folders...
rm -rf $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Azenqos

echo == Copying new plugin from this folder...
rm -f `pwd`/Azenqos $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Azenqos
ln -s `pwd`/Azenqos $HOME/.local/share/QGIS/QGIS3/profiles/default/python/plugins/Azenqos
exit_if_failed

ls -l $HOME/.local/share/QGIS/QGIS3/profiles/default/QGIS/QGIS3.ini
exit_if_failed

sudo apt-get -y install crudini
exit_if_failed

crudini --set $HOME/.local/share/QGIS/QGIS3/profiles/default/QGIS/QGIS3.ini PythonPlugins Azenqos true
exit_if_failed

echo
echo === INSTAL SUCCESS - you can start QGIS now
echo "If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin"

