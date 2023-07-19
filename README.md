# pyopenVA_GUI

Graphical User Interface for the openVA tool implemented in Python.

## Details

* Developing with PyQt5, building with [cx_Freeze](https://cx-freeze.readthedocs.io/en/latest/index.html)

* Building app/executable 

  + Windows:  `python setup.py bdist_msi`
  + Mac: `python setup.py bdist_dmg`

* Build docs with: `sphinx-build -b html docs/source/ pyopenva/docs -a`

## To Do

* Set up splash screen?

* Can we set up continuous integration service that builds executables/apps and
adds them (for different OS's) to this site as releases?  Something like [https://github.com/ncipollo/release-action](https://github.com/ncipollo/release-action)

* Unit tests for Qt: [pytest-qt](https://pytest-qt.readthedocs.io/en/latest/intro.html)


