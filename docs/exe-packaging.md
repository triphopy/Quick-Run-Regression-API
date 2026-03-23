# EXE Packaging

## Goal

Build a Windows `.exe` launcher so teammates can start the app without manually running Python or Streamlit commands.

Recommended packaging style:

- `PyInstaller`
- `--onedir`
- launcher executable plus bundled resources

`--onedir` is recommended over `--onefile` for this project because it is more reliable with Streamlit, Robot Framework, and bundled resource folders.

## What The Launcher Does

The launcher in [launcher.py](../launcher.py):

- checks whether port `8501` is already in use
- opens the existing local app if it is already running
- sets runtime and resource paths for bundled execution
- starts Streamlit with the bundled `app.py`
- opens the browser automatically

## Install Build Dependency

```powershell
python -m pip install pyinstaller
```

## One-Click Build

You can use the included batch file:

```powershell
build_exe.bat
```

The script will:

- detect `py` or `python`
- install `pyinstaller` if needed
- build the launcher into `dist/SONIC`
- copy `packaging/README-for-user.txt` into `dist/SONIC/README-for-user.txt`

## Recommended Build Command

Run this from the project root:

```powershell
pyinstaller launcher.py `
  --name SONIC `
  --onedir `
  --clean `
  --noconfirm `
  --add-data "app.py;." `
  --add-data "assets;assets" `
  --add-data "docs;docs" `
  --add-data "robot;robot" `
  --add-data "src;src" `
  --hidden-import streamlit.web.cli `
  --hidden-import robot `
  --collect-all streamlit `
  --collect-all robot
```

## Output

After build, the launcher should be in:

```text
dist/SONIC/SONIC.exe
```

Distribute the whole `dist/SONIC` folder to users, not only the `.exe` file.

The user-facing quick-start text is maintained in:

```text
packaging/README-for-user.txt
```

and is copied into `dist/SONIC` automatically during build.

## Notes

- The launcher uses `data/` next to the executable for runtime files.
- Bundled resources such as `assets/`, `robot/`, and `src/` are read from the packaged resource folder.
- If port `8501` is already in use, the launcher will open the browser to the running app instead of starting a second copy.
- SmartScreen or antivirus warnings may appear on some Windows machines for unsigned executables.

## Recommended First Test

1. Build with PyInstaller
2. Open `dist/SONIC/SONIC.exe`
3. Confirm the browser opens at `http://localhost:8501`
4. Load `Demo Mix`
5. Run the sample and verify:
   - Dashboard works
   - Log works
   - `data/output` is created next to the executable
