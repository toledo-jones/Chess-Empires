import cx_Freeze

executables = [cx_Freeze.Executable('main.py')]

cx_Freeze.setup(
    name="Chess-Empires",
    options={"build_exe": {
                            "build_exe": ".//build",
                            "packages": ["pygame"],
                           "include_files": ["assets"],
                                "excludes": ["cv2"]}},
    executables=executables
)