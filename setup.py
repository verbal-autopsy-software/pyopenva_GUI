"""
cx_Freeze script for building pyopenVA App.  Build the windows installer
with

python setup.py bdist_msi

and the macOS installer with

python setup.py bdist_dmg
"""

import sys
from cx_Freeze import Executable, setup
import os
import subprocess

# create docs
subprocess.run(["sphinx-build", "-b", "html", "docs/source",
                "pyopenva/docs", "-a"])

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(
        os.path.join(here, "pyopenva", "__version__.py"),
        mode="r",
        encoding="utf-8") as f:
    exec(f.read(), about)

include_files = []
include_files.append("pyopenva/data")
include_files.append("pyopenva/docs")

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

build_exe_options = {
    "excludes": ["tkinter"],
    "include_files": include_files,
    # "zip_include_packages": ["PyQt5"],
}

bdist_mac_options = {
    "bundle_name": "pyopenVA",
    "iconfile": "pyopenva/icons/openva-logo.ico",
}

bdist_dmg_options = {
    "volume_label": "pyopenVA",
}

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("MyProgramMenu", "ProgramMenuFolder", "MYPROG~1|My Program"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None,
         "openVA App for verbal autopsy data", "IconId", None),
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
    # "upgrade_code": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}",
}

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

setup(
    name="pyopenva",
    version=about["__version__"],
    description=about["__description__"],
    options={
        "build_exe": build_exe_options,
        # "bdist_msi": bdist_msi_options,
        "bdist_mac": bdist_mac_options,
        "bdist_dmg": bdist_dmg_options,
    },
    executables=executables,
)
