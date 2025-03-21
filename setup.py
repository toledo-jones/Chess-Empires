import cx_Freeze

executables = [cx_Freeze.Executable('main.py', base="Win32GUI")]

cx_Freeze.setup(
    name="Chess Empires",
    options={"build_exe": {
        "packages": ["pygame"],
        "include_files": [("files", "files")],  # Ensure correct copying
        "excludes": ["cv2"]
    }},
    executables=executables
)
