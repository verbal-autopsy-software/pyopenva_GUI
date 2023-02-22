"""
A simple setup script to create an executable using PyQt5. This also
demonstrates the method for creating a Windows executable that does not have
an associated console.

PyQt5app.py is a very simple type of PyQt5 application

Run the build process by running the command 'python setup.py build'

If everything works well you should find a subdirectory in the build
subdirectory that contains the files needed to run the application
"""

import sys
import os
from cx_Freeze import Executable, setup

try:
    from cx_Freeze.hooks import get_qt_plugins_paths
except ImportError:
    include_files = []
else:
    # Inclusion of extra plugins (new in cx_Freeze 6.8b2)
    # cx_Freeze imports automatically the following plugins depending of the
    # use of some modules:
    # imageformats - QtGui
    # platforms - QtGui
    # mediaservice - QtMultimedia
    # printsupport - QtPrintSupport
    #
    # So, "platforms" is used here for demonstration purposes.
    include_files = get_qt_plugins_paths("PyQt5", "platforms")

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {
    "excludes": ["tkinter"],
    "include_files": include_files,
    "zip_include_packages": ["PyQt5"],
    "packages": ["pyopenva", "interva", "vacheck", "pycrossva", "insilicova"]
    #"includes": ["pyopenva"]
}

bdist_mac_options = {
    "bundle_name": "Test",
}

bdist_dmg_options = {
    "volume_label": "TEST",
}

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "openVA App for verbal autopsy data", "IconId", None),
    ],
    "Icon": [
        ("IconId", "pyopenva/icons/openva-logo.ico"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    # "environment_variables": [
    #     ("E_MYAPP_VAR", "=-*MYAPP_VAR", "1", "TARGETDIR")
    # ],
    #"upgrade_code": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}",
}

#build_exe_options = {"excludes": ["tkinter"], "include_msvcr": True}

executables = [
        Executable(
            "pyopenva/main.py",
             base=base,
            icon="pyopenva/icons/openva-logo.ico",
            shortcut_name="pyopenva",
            shortcut_dir="DesktopFolder",
            target_name="pyopenva"
        ),
    ]

#executables = [Executable("pyopenva/main.py", base=None, target_name="pyopenva")]

setup(
    name="pyopenva",
    version="0.1",
    description="openVA App for analyzing Verbal Autopsy data",
    options={
        "build_exe": build_exe_options,
        #"bdist_msi": bdist_msi_options,
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
    },
    executables=executables,
)
