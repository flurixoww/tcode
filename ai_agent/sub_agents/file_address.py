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
        refered_file_names = []
        start_index = text.find(char1) + 1

        end_index = text[start_index:].find(char2)

        refered_file_names.append(text[start_index : start_index + end_index])

        return refered_file_names

    except Exception as e:
        raise RuntimeError(f"File finding was unsuccessfull. {e}") from e
