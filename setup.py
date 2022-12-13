import cx_Freeze

executables = [cx_Freeze.Executable('main.py')]

cx_Freeze.setup(
    name="Chess Empires",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["resources"]}},
    executables=executables
)