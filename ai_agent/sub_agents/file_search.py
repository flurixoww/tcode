# Imports
import os

import chromadb


# Algorithm for extracting file's name and content
def file_info():
    files = []
    files_content = []

    for file in os.listdir():
        if os.path.isfile(file):
            files.append(file)
            with open(file, "r", encoding="utf-8") as f:
                file_content = f.read()
                files_content.append(file_content)
    return files, files_content


def file_distance(ids, documents, prompt):
    # Chroma initialization
    chroma_client = chromadb.Client()

    # Chroma file architecture
    files_collection = chroma_client.create_collection(name="files")

    # Importing files and content of the files into chroma file architecture
    files_collection.add(ids=ids, documents=documents)

    # Chroma RAG model settings and initialization
    result = files_collection.query(
        query_texts=prompt,
        n_results=3,
        include=["distances"],
    )
    return result["ids"], result["distances"]


# Needs improvment, if distance of all documents is >1.25, we should return 3 most plausible
# At least 3 documents should be present.
def likely_files(ids, distances):

    check = len(ids[0])

    for file_i in range(check - 1):
        if distances[0][file_i] < 1.25:
            return ids[0][file_i]
