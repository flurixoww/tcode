from pathlib import Path


def file_opener(file_name):
    path = Path(file_name).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    return path.read_text(encoding="utf-8")
