from sys import platform
import PyInstaller.__main__

if platform == "linux":
    PyInstaller.__main__.run([
        "src/main/python/main.py",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name 'pyopenva'",
        "icon='src/main/icons/openva-logo.png'"
        ])
elif platform == "darwin":
    PyInstaller.__main__.run([
        "src/main/python/main.py",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name",
        "pyopenva",
        "--osx-bundle-identifier",
        "net.openva.pyopenva",
        "--icon",
        "src/main/icons/openva-logo.png"
    ])
elif platform in ["cygwin", "win32"]:
    PyInstaller.__main__.run([
        "src/main/python/main.py",
        "--clean",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name 'pyopenva'",
        "icon='src/main/icons/openva-logo.png'"
    ])
