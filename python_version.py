import importlib.util

with open(r"Daily Monitoring.exe_extracted\PYZ.pyz_extracted\ui\connections_view.pyc", "rb") as f:
    magic = f.read(4)

print(magic)