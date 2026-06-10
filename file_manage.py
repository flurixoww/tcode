import pathlib

# File management backend


def file_opener(file_name):
    with open(pathlib.Path(file_name), "r", encoding="utf-8") as file:
        content = file.read()
        return content
