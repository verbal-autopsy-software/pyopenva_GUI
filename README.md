# pyopenVA_GUI

Graphical User Interface for the openVA tool implemented in Python.

## Details

* Developing with PyQt5, building with [cx_Freeze](https://cx-freeze.readthedocs.io/en/latest/index.html)

* Building app/executable 

  + Windows:  `python setup.py bdist_msi`
  + Mac: `python setup.py bdist_dmg`

* Build docs with: `sphinx-build -b html docs/source/ pyopenva/docs -a`
  + this is included in setup.py

## Known Bugs

* Fixed:
  + GUI crashes on Mac when trying to view help documentation
    - cx_Freeze [Issue 933](https://github.com/marcelotduarte/cx_Freeze/issues/933)
    - fixed with cx_Freeze version 6.15.12
