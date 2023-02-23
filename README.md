# pyopenVA_GUI

Graphical User Interface for the openVA tool implemented in Python.

## Details

* Developing with PyQt5 with Python 3.9.10 

* Building app/executable with `python setup.py build` (using [cx_Freeze](https://cx-freeze.readthedocs.io/en/latest/index.html) package)

  + includes OS-specific calls
  + set up splash screen?
  + *note*: for build_exe, it is necessary to manually copy the `PyQt5\\Qt5\\bin` and 
  `matplotlib.libs` folders (from site-package of Python or venv) into the lib folder of the build

## To Do

* Can we set up continuous integration service that builds executables/apps and
adds them (for different OS's) to this site as releases?  (Probably not since the file size will be massive)

* Unit tests for Qt: [pytest-qt](https://pytest-qt.readthedocs.io/en/latest/intro.html)


