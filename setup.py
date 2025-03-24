import cx_Freeze

executables = [cx_Freeze.Executable("main.py")]
cx_Freeze.setup(
    name="Chess Empires",
    options={
        "build_exe": {
            "packages": ["pygame"],
            "include_files": [("files", "files")],
            "excludes": ["cv2"],
        }
    },
    executables=executables,
)

# python setup.py bdist_mac
