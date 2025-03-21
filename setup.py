import cx_Freeze

executables = [cx_Freeze.Executable('main.py')]  # No base needed for macOS

cx_Freeze.setup(
    name="Chess Empires",
    options={"build_exe": {
        "packages": ["pygame"],
        "include_files": [("files", "files")],  # Ensure correct file copying
        "excludes": ["cv2"]
    }},
    executables=executables
)
