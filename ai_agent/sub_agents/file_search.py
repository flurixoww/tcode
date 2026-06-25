# Imports
import os

import chromadb
import langchain_text_splitters
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter

# Initialization of chroma client -> initialization of code aware splitter
# Splitting files in chunks and organizing them -> Uploading those chunks in the RAG model
# Find the file distances -> Pick the most likely files


def chroma_client_initialization() -> chromadb.Collection:
    """
    Initializes chroma client.

    Args:
        None

    Returns:
        chromadb.Collection: Prepared collection with the files and their content.

    Raises:
        RuntimeError: If initialization of the model was unsuccessful.
    """

    try:
        # Chroma initialization
        chroma_client = chromadb.PersistentClient(path="./chroma_db")

        # Chroma file architecture
        files_collection = chroma_client.get_or_create_collection(name="codebase_rag")

        return files_collection
    except Exception as e:
        raise RuntimeError(f"The initialization of the model failed {e}") from e


def code_aware_splitter() -> langchain_text_splitters.RecursiveCharacterTextSplitter:
    """
    Initializes code aware splitters to split the code for the RAG model

    Args:
        None

    Retrurns:
        RecursiveCharacterTextSplitter: Splitter model

    Raises:
        RuntimeError: Something went wrong during the initialization of splitting model.
    """

    try:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=200
        )
        return splitter
    except Exception as e:
        raise RuntimeError(
            f"Something went wrong during initialization of code aware splitter {e}"
        ) from e


def ignored_files_file_info(filepath="ignore_rules.txt") -> str:
    """
    Made for the file_info function so the user can make their own file ignore.

    Args:
        filepath("ignore_rules.txt"): File with the ignored files/directories.

    Returns:
        ignored_files(str): files in a correct, readable for python ways.

    Raises:
        RuntimeError: If there was something wrong with the file.
    """

    try:
        with open(filepath, "r") as f:
            ignored_files = ""
            for line in f:
                if not line.startswith("#"):
                    ignored_files = line.strip()
        return ignored_files
    except Exception as e:
        raise RuntimeError(
            f"There was a problem when trying to import data from ignore_rules {e}"
        ) from e


# Needs to be divided into seperate functions
def file_info(
    directory_path: str, splitter: RecursiveCharacterTextSplitter, ignored_files: str
) -> tuple[list[str], list[dict], list[str]]:
    """
    Extracts the names and the content of the files in the current directory and divides it into chunks.

    Args:
        directory_path(str): Path to the directory from which all the files are going to be searched.
        splitter(RecursiveCharacterTextSplitter): Splitter model
        ignored_files(str): Files to ignore when walking through the directory.

    Returns:
        tuple: A tuple containing three lists:
            documents (str): The chunks of the files.
            metadatas (dict): File path to a certain chunk.
            ids (str): Unique name for every chunk to keep database organized.

    Raises:
        RuntimeError: If file receiving was unsuccessful.
    """

    try:
        documents = []
        metadatas = []
        ids = []

        for root, _, files in os.walk(directory_path):
            _[:] = [d for d in _ if not d.startswith(".") and d not in ignored_files]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_content = f.read()
                    try:
                        chunks = splitter.split_text(
                            code_content
                        )  # Look up how it looks
                        # Tf is going on here????
                        for i, chunk in enumerate(chunks):
                            documents.append(chunk)
                            metadatas.append(
                                {"source_file": file_path, "chunk_index": i}
                            )
                            ids.append(f"{file_path}_chunk_{i}")
                    except Exception as e:
                        raise RuntimeError(
                            f"Error occured when splitting the code into chunks.{e}"
                        ) from e
        return documents, metadatas, ids
    except Exception as e:
        raise RuntimeError(f"File extraction was unsuccessful: {e}") from e


def chromadb_batch_upsert(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    files_collection: chromadb.Collection,
):
    """
    Args:
        documents(list[str]): The chunks of the files
        metadatas(list[dict]): File path to a certain chunk.
        ids(list[str]): Unique name for every chunk to keep database organized.
        files_collection(chromadb.Collection): Chromadb collection architecture.
    Returns:
        None
    Raises:
        RuntimeError: When there was an error when trying to push the chunks.
    """
    try:
        if documents:
            files_collection.upsert(
                documents=documents,
                metadatas=metadatas,  # type: ignore
                ids=ids,
            )
            print(f"Successfully indexed {len(documents)} chunks.")
    except Exception as e:
        raise RuntimeError(
            f"Error occured when trying to index chunks into the rag file collection {e}"
        ) from e


def find_closest_files(
    files_collection: chromadb.Collection, prompt: str
) -> tuple[list[str], list[float]]:
    """
    Using RAG model finds the likability of the files to the prompt.

    Args:
        files_collection (chromadb.Collection): Chroma file architecture with already imported files.
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

    likely_files = []
    try:
        for file in range(len(file_ids)):
            if distances[file] <= 1.3:
                likely_files.append(file_ids[file])
        return likely_files

    except Exception as e:
        raise RuntimeError(
            f"Error occured during picking of the closest files {e}"
        ) from e
