import os


# Improve it a lil bit.
def exact_file_address(text: str, char1="@", char2=" ") -> list[str]:
    """
    Finds reference to the file in the text.

    Args:
        text (str): The users prompt from which we will be trying to find the needed file.
        char1 ("@"): Default character to refer to a certain file.
        char2 (" "): Refering stops when we hit the space character.

    Returns:
        list[str]: list of refered files in the text.

    Raises:
        RuntimeError: When it failed to find the refered files.
    """

    try:
        text = text + " "
        files = []
        indices = [index for index, char in enumerate(text) if char == "@"]
        if len(indices) <= 0:
            return []
        end_index = indices[0]
        for index in indices:
            for char in range(len(text[end_index:])):
                if text[char + end_index] == char2 and char + end_index > index:
                    files.append(text[index + 1 : char + end_index])
                    end_index = char + end_index
                    break
        return files

    except Exception as e:
        raise RuntimeError(f"File finding was unsuccessfull. {e}") from e


def exact_file_path(file_names: list[str], ignored_files: list[str]) -> list[str]:
    """
    Finds a full path to the file found in exact_file_address()

    Args:
        file_names(list[str]): Names of the files without full path to the directory.
        ignored_files(list[str]): List of exception for the searching algorithm.
    Returns:
        list[str]: Names of the files with the full path to the directory.

    Raises:
        RuntimeError: When there was a problem finding full path to the file.
    """
    try:
        full_paths = []
        for file in file_names:
            for root, _, files in os.walk(os.getcwd()):
                _[:] = [
                    d for d in _ if not d.startswith(".") and d not in ignored_files
                ]
                if file in files:
                    full_paths.append(os.path.abspath(os.path.join(root, file)))
        return full_paths
    except Exception as e:
        raise RuntimeError(
            f"There was a problem finding a full path to the file {e}"
        ) from e
