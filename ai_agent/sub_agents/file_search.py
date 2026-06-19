# Imports
import os

import chromadb


def file_info() -> tuple[list[str], list[str]]:
    """
    Extracts the names and the content of the files in the current directory.

    Args:
        None

    Returns:
        tuple: A tuple containing two lists:
            files: The list containing names of the available files in the current directory.
            files_content: The list containing content of the files.

    Raises:
        RuntimeError: If file receiving was unsuccessful.
    """

    try:
        files = []
        files_content = []

        for file in os.listdir():
            if os.path.isfile(file):
                files.append(file)
                with open(file, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    files_content.append(file_content)
        return files, files_content

    except Exception as e:
        raise RuntimeError(f"File extraction was unsuccessful: {e}") from e


def chroma_client_initialization(ids: list, documents: list) -> chromadb.Collection:
    """
    Initializes chroma and loads documents into the structure

    Args:
        ids (list): The list of possible files.
        documents (list): The list of content of files.

    Returns:
        chromadb.Collection: Prepared collection with the files and their content.

    Raises:
        RuntimeError: If initialization of the model was unsuccessful.
    """

    try:
        # Chroma initialization
        chroma_client = chromadb.Client()

        # Chroma file architecture
        files_collection = chroma_client.get_or_create_collection(name="files")

        # Importing files and content of the files into chroma file architecture
        files_collection.add(ids=ids, documents=documents)

        return files_collection
    except Exception as e:
        raise RuntimeError(f"The initialization of the model failed {e}") from e


def file_distance(
    files_collection: chromadb.Collection, prompt: str
) -> tuple[list[str], list[float]]:
    """
    Using RAG model finds the likability of the files to the prompt.

    Args:
        files_collection (chromadb.Collection): Chroma file architecture with already imported files
        prompt (str): The user's prompt.

    Returns:
        tuple: A tuple containing two lists:
            result['ids']: Contains the ids of the most relevant files.
            result['distances']: Contains the possibility of the file connection
            to the prompt in order respective to the ids.
    Raiess:
        RuntimeError: If model didn't work
    """
    try:
        # Chroma RAG model settings and initialization
        result = files_collection.query(
            query_texts=prompt,
            include=["distances"],
        )

        if result["distances"] is not None:
            return result["ids"][0], result["distances"][0]
        else:
            return result["ids"][0], []

    except Exception as e:
        raise RuntimeError(f"Error occured when initializing a model. {e}") from e


def likely_files(file_ids: list[str], distances: list[float]) -> list[str]:
    """
    Picks the closest files to the prompt.

    Args:
        file_ids (list): File names.
        distances (list): File distance to the prompt, with the same order as file ids.

    Returns:
        list: Name of the files from the least to the biggest distance.

    Raises:
        RuntimeError: If there was a problem picking a closest file.
    """

    # To be improved in the future
    likely_files = []
    try:
        for file in range(len(file_ids)):
            if distances[file] <= 1.25:
                likely_files.append(file_ids[file])
            if len(likely_files) < 3 and distances[file] > 1.25:
                likely_files.append(file_ids[file])
        return likely_files

    except Exception as e:
        raise RuntimeError(
            f"Error occured during picking of the closest files {e}"
        ) from e
