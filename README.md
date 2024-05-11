# pyOpenVA GUI

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


# Acknowledgements & Notes

* This application is a reimplementation of the **R** package [**openVA: Automated Method for Verbal Autopsy**](https://cran.r-project.org/package=openVA) by Zehang Richard Li, Jason Thomas, Tyler H. McCormick, and Samuel J. Clark.

* The purpose of this reimplementation is to make the openVA tools: 1) easy to install, 2) much faster, and 3) much easier to operate using a point-and-click graphical user interface.

* [Jason Thomas](https://ipr.osu.edu/people/thomas.3912) is mostly responsible for the code in this package, with help from Sherry Zhao and Eungang Choi. Samual J. Clark, with input from Robert Mswia and Martin Bratchi, created the idea for this application and oversaw its creation. The CRVS Improvemenet program at [Vital Strategies](https://www.vitalstrategies.org) supported the creation of this application.


# Known Bugs

* Fixed:
  + GUI crashes on Mac when trying to view help documentation
    - cx_Freeze [Issue 933](https://github.com/marcelotduarte/cx_Freeze/issues/933)
    - fixed with cx_Freeze version 6.15.12
