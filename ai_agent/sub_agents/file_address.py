"""Module for extracting referred file names from text and resolving their absolute paths."""

import os


def exact_file_address(text: str, char1: str = "@", char2: str = " ") -> list[str]:
    """Finds references to files in the text.

    Args:
        text: The user's prompt from which we extract referred files.
        char1: Prefix character indicating the start of a file reference.
        char2: Character indicating the end of a file reference.

    Returns:
        A list of referred file names extracted from the text.

    Raises:
        RuntimeError: If file reference extraction fails.
    """
    try:
        text = text + " "
        files = []

        # Respect the 'char1' parameter instead of hardcoding '@'
        indices = [index for index, char in enumerate(text) if char == char1]
        if not indices:
            return []

        end_index = indices[0]
        for index in indices:
            for char_offset in range(len(text[end_index:])):
                current_char_idx = char_offset + end_index
                if text[current_char_idx] == char2 and current_char_idx > index:
                    files.append(text[index + 1 : current_char_idx])
                    end_index = current_char_idx
                    break
        return files

    except Exception as e:
        raise RuntimeError(f"File finding was unsuccessful: {e}") from e


def exact_file_path(file_names: list[str], ignored_files: list[str]) -> list[str]:
    """Finds the absolute path to each file in the workspace.

    Args:
        file_names: Names of files without their directory paths.
        ignored_files: List of directory or file names to ignore during search.

    Returns:
        A list of absolute paths to the found files.

    Raises:
        RuntimeError: If finding the paths fails.
    """
    try:
        full_paths = []
        for file in file_names:
            for root, dirs, files in os.walk(os.getcwd()):
                # Rename standard '_' walk variable to 'dirs' for clarity
                dirs[:] = [
                    d for d in dirs if not d.startswith(".") and d not in ignored_files
                ]
                if file in files:
                    full_paths.append(os.path.abspath(os.path.join(root, file)))
        return full_paths
    except Exception as e:
        raise RuntimeError(
            f"There was a problem finding a full path to the file: {e}"
        ) from e
