"""Module for managing codebase indexing and semantic search using ChromaDB and LangChain."""

import os

import chromadb
import langchain_text_splitters
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter


def chroma_client_initialization(name: str = "codebase_rag") -> chromadb.Collection:
    """Initializes the ChromaDB persistent client and collection.

    Args:
        name: Name for the Chroma collection.

    Returns:
        Prepared collection for indexing files and their content.

    Raises:
        RuntimeError: If client or collection initialization fails.
    """
    try:
        # Chroma initialization
        chroma_client = chromadb.PersistentClient(path="./chroma_db")

        # Chroma file architecture
        files_collection = chroma_client.get_or_create_collection(name=name)

        return files_collection
    except Exception as e:
        raise RuntimeError(f"The initialization of the model failed: {e}") from e


def code_aware_splitter() -> langchain_text_splitters.RecursiveCharacterTextSplitter:
    """Initializes the code-aware text splitter for Python.

    Returns:
        The recursive character text splitter.

    Raises:
        RuntimeError: If initialization of the splitting model fails.
    """
    try:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=200
        )
        return splitter
    except Exception as e:
        raise RuntimeError(
            f"Something went wrong during initialization of code aware splitter: {e}"
        ) from e


def ignored_files_info(filepath: str = "ignore_rules.txt") -> list[str]:
    """Reads the files or directories to ignore from a rules file.

    Args:
        filepath: Path to the file containing ignore rules.

    Returns:
        A list of file and directory names to ignore.

    Raises:
        RuntimeError: If reading the ignore rules file fails.
    """
    try:
        with open(filepath, "r") as f:
            ignored_files = []
            for line in f:
                if not line.startswith("#"):
                    ignored_files.append(line.strip())
        return ignored_files
    except Exception as e:
        raise RuntimeError(
            f"There was a problem when trying to import data from ignore_rules: {e}"
        ) from e


# TODO(developer): Consider refactoring this function into smaller, single-responsibility functions.
def file_info(
    directory_path: str,
    splitter: RecursiveCharacterTextSplitter,
    ignored_files: list[str],
) -> tuple[list[str], list[dict], list[str]]:
    """Extracts codebase file contents and splits them into text chunks.

    Args:
        directory_path: Path to the directory to walk through.
        splitter: Text splitter model.
        ignored_files: Files and directories to ignore when walking.

    Returns:
        A tuple containing three lists:
            - documents: The split text chunks.
            - metadatas: Dictionaries mapping each chunk to its source file and index.
            - ids: Unique string IDs for every chunk.

    Raises:
        RuntimeError: If file processing or text splitting fails.
    """
    try:
        documents = []
        metadatas = []
        ids = []

        for root, dirs, files in os.walk(directory_path):
            # Prune hidden and ignored directories in-place using 'dirs' instead of '_'
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ignored_files]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code_content = f.read()
                    try:
                        chunks = splitter.split_text(code_content)
                        for i, chunk in enumerate(chunks):
                            documents.append(chunk)
                            metadatas.append(
                                {"source_file": file_path, "chunk_index": i}
                            )
                            ids.append(f"{file_path}_chunk_{i}")
                    except Exception as e:
                        raise RuntimeError(
                            f"Error occurred when splitting the code into chunks: {e}"
                        ) from e
        return documents, metadatas, ids
    except Exception as e:
        raise RuntimeError(f"File extraction was unsuccessful: {e}") from e


def chromadb_batch_upsert(
    documents: list[str],
    metadatas: list[dict],
    ids: list[str],
    files_collection: chromadb.Collection,
) -> None:
    """Upserts the document chunks and metadata into the Chroma collection.

    Args:
        documents: The text chunks to upload.
        metadatas: Metadata dictionaries for each chunk.
        ids: Unique string IDs for each chunk.
        files_collection: The target ChromaDB collection.

    Raises:
        RuntimeError: If the collection upsert fails.
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
            f"Error occurred when trying to index chunks into the rag file collection: {e}"
        ) from e


def find_closest_files(
    files_collection: chromadb.Collection, prompt: str
) -> tuple[list[str], list[float], list[str]]:
    """Finds chunks in the Chroma collection that are most semantically similar to the prompt.

    Args:
        files_collection: The Chroma collection containing indexed files.
        prompt: The query string to search for.

    Returns:
        A tuple containing:
            - A list of matching chunk IDs.
            - A list of match distance scores.
            - A list of document texts for the matching chunks.

    Raises:
        RuntimeError: If the query fails to execute.
    """
    try:
        result = files_collection.query(
            query_texts=prompt,
            include=["documents", "distances"],
        )

        if result["distances"] and result["documents"] is not None:
            return result["ids"][0], result["distances"][0], result["documents"][0]
        else:
            return result["ids"][0], [], []

    except Exception as e:
        raise RuntimeError(f"Error occurred when initializing a model: {e}") from e


def likely_files(
    file_ids: list[str], distances: list[float], documents: list[str]
) -> dict[str, str]:
    """Filters and selects the most relevant files based on search distances.

    Args:
        file_ids: List of chunk IDs.
        distances: Semantic distance scores corresponding to the chunk IDs.
        documents: The source text contents of each chunk.

    Returns:
        A dictionary mapping the selected chunk IDs to their text content.

    Raises:
        RuntimeError: If selection logic encounters an error.
    """
    likely_files_dict = {}
    try:
        temp = 0.0
        for i in range(len(file_ids)):
            if i == 0:
                likely_files_dict[file_ids[i]] = documents[i]
                temp = distances[i]
            elif distances[i] - temp <= 0.194:
                likely_files_dict[file_ids[i]] = documents[i]
                temp = distances[i]
        return likely_files_dict

    except Exception as e:
        raise RuntimeError(
            f"Error occurred during picking of the closest files: {e}"
        ) from e
