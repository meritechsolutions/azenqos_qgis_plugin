AZENQOS Log Replay QGIS Plugin
==============================

Install this plugin into QGIS to analyze AZENQOS '.azm' test logs: analyze Layer-3 Signalling, Events, 5GNR/LTE/WCDMA/GSM mesurements - all syncing with the QGIS map plot of your test log captured from the [AZENQOS Android Drivetest tool](https://www2.azenqos.com/) app.


Installation instructions for Windows
-------------------------------------

- Install *QGIS Standalone Installer Version 3.10 or 3.16 (64 bit)* from: <https://qgis.org/en/site/forusers/download.html> > Long Term Release > QGIS Standalone Installer Version 3.16
- If first install, open QGIS, complete first time setup then exit (we just want it to create required folders).
- Close QGIS if it is open.
- Click on near top-right of this github page: 'Code' button > 'Download ZIP' - save it to your computer, extract the zip to a folder.
- In the extracted folder, double-click on <pre>install_azenqos_plugin.bat</pre> - it must show 'SUCCESS', otherwise fix as per error message shown.
- If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin
- Press on the AZENQOS icon button in toolbar (or in 'Plugins') - the analyzer window will launch.
- In the analyzer window, go to File > Open log file... to choose a .azm log file to analyze.
- After a log has been opened. Go to Presentation to open each required analyzer window - like Signalling > Layer-3 Messages.

- Repeat the same steps above when you want to upgrade the plugin to a new version (version is shown at top-right of analyzer window).


Installation instructions for Ubuntu GNU/Linux
-------------------------------------
- Install QGIS Long Term Release on Ubuntu, open and complete first time setup if first run.
- Close QGIS if it is open.
- Click on near top-right of this github page: 'Code' button > 'Download ZIP' - save it to your computer, extract the zip to a folder. (Or if you know how to use `git` then git clone this repo)
- Open a terminal to that folder then run <pre>./install_azenqos_plugin_ubuntu.sh</pre> - it must show 'SUCCESS', otherwise fix as per error message shown. (Note that this makes a link to contents of this folder so dont delete this folder unless you're going to re-install from a new version)
- If first time, in QGIS, go to 'Plugins' > 'Manage and install plugins' > 'Installed' and enable the 'Azenqos' plugin
- Press on the AZENQOS icon button in toolbar (or in 'Plugins') to choose a .azm log file to analyze.
- Repeat the same when you want to upgrade the plugin

Using Standlone mode to launch without QGIS (Developer mode)
------------------------------------------------------------

- Run:
`pip3 install -r requirements-dev.txt`

- Install pyqt5
  - If you are on Windows run:
  `pip3 install -r requirements-dev-windows.txt`
  - If you are on Ubuntu run:
  `sudo apt install python3-pyqt5`
  
- Launch analyzer in standalone mode:
`cd Azenqos`
`python3 ui_test_main_window.py`


Running tests (install developer mode dependencies in previous step first)
----------------------------------------------------------------

- Non-ui tests: run `./test.sh` in 'Azenqos' folder for GNU/Linux, otherwise use pytest.
- Testing specific ui dialogs/windows: run ui_test_* files with python3, for example - to launch main window in standalone (non-QGIS) mode - do: `python3 ui_test_main_window.py`
- Testing specific QGIS functions at start of pressing the qgis plugin button (instead of launching the main_window): create a file named `debug_qgis_pyexec` in this folder and put your python code to test in there, for example: `import qgis_test_csv_layer`. Then launch QGIS, tap on the azenqos plugin icon in toolbar - it would run your code only.


License
-------

- Released under the GNU GPL version 2. Please see [LICENSE](LICENSE) file.

Copyright (C) 2019-2020 Freewill FX Co., Ltd.

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


Special thanks and notices
--------------------------

- This project (which is licensed under the GNU GPLv2 - same as Wireshark) uses `tshark` and `text2pcap` utilities from the Wireshark project. Full credit and thanks to the Wireshark developers for their great work. Please see [wireshark_LICENSE](wireshark_LICENSE) file for its license and [wireshark_SOURCE](wireshark_SOURCE) for its source.

