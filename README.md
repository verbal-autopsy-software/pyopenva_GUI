# pyopenVA GUI

Graphical User Interface for the openVA tool implemented in Python.  

* assigns causes of death to data collected with the 2016 WHO VA instrument

* algorithm options: InSilicoVA & InterVA5


# Downloading and Installing the GUI

Installer files are available for Windows (msi) and macOS (dmg) on the [Releases](https://github.com/verbal-autopsy-software/pyopenva_GUI/releases) page.

#### Additonal steps for macOS

Since we are not official Apple developers (and the GUI is not available in the App store), macOS users need the following steps
to run the GUI (from the downloaded dmg installer file)

* In a Finder window, double-click the pyopenVA.dmg file, which should mount the image and show the pyopeVA.app icon -- do NOT double click the pyopenVA.app icon

* Open a Terminal: Applications &rarr; Utilities &rarr; Terminal.app

* Run the following command in the terminal:
  
  `xattr -cr /path/to/pyopenVA.app`
  
  (the path is probably /Volumes/pyopenVA/pyopenVA.app)

* Run the following command in the terminal:

  `open /path/to/pyopenVA.app`


# Build Details

* Developing with PyQt5, building with [cx_Freeze](https://cx-freeze.readthedocs.io/en/latest/index.html)

* Building app/executable 

  + Windows:  `python setup.py bdist_msi`
  + Mac: `python setup.py bdist_dmg`

* Build docs with: `sphinx-build -b html docs/source/ pyopenva/docs -a`
  + this is included in setup.py

# Known Bugs

* Fixed:
  + GUI crashes on Mac when trying to view help documentation
    - cx_Freeze [Issue 933](https://github.com/marcelotduarte/cx_Freeze/issues/933)
    - fixed with cx_Freeze version 6.15.12
