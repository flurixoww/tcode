"""Module for evaluating codebase retrieval performance against a synthetic test dataset."""

import json
import os
from typing import Any

import chromadb
import pandas as pd

from ai_agent.sub_agents.file_search import (
    chroma_client_initialization,
    chromadb_batch_upsert,
    code_aware_splitter,
    file_info,
    find_closest_files,
    ignored_files_info,
)


def _clean_filepath(path_string: str) -> str:
    """Extracts the base filename from a path string, ensuring .py extension remains intact.

    Args:
        path_string: The file path to clean.

    Returns:
        The clean base filename.

    Raises:
        RuntimeError: If file path cleaning fails.
    """
    try:
        if ".py" in path_string:
            path_string = path_string.split(".py")[0] + ".py"
        return os.path.basename(path_string)
    except Exception as e:
        raise RuntimeError(f"Error cleaning file path '{path_string}': {e}") from e


def _max_correct_file(
    clean_closest_files: list[str], file_distances: list[float], target_file: str
) -> float:
    """Finds the distance/score of the matched target file.

    Args:
        clean_closest_files: List of clean file names retrieved.
        file_distances: Semantic search distance/similarity scores for the retrieved files.
        target_file: The expected correct file name.

    Returns:
        The score of the matched correct file, or 0.0 if not found.

    Raises:
        RuntimeError: If calculation of the max correct file distance fails.
    """
    try:
        file_distance = 0.0
        for file_name, dist in zip(clean_closest_files, file_distances):
            if file_name == target_file and dist > 0.0:
                file_distance = dist
        return file_distance
    except Exception as e:
        raise RuntimeError(
            f"Error calculating max correct file distance for target '{target_file}': {e}"
        ) from e


def _min_incorrect_file(
    clean_closest_files: list[str], file_distances: list[float], target_file: str
) -> float:
    """Finds the distance/score of the first incorrect file retrieved.

    Args:
        clean_closest_files: List of clean file names retrieved.
        file_distances: Semantic search distance/similarity scores for the retrieved files.
        target_file: The expected correct file name.

    Returns:
        The score of the first incorrect file, or 0.0 if all retrieved files are correct.

    Raises:
        RuntimeError: If calculation of the min incorrect file distance fails.
    """
    try:
        for file_name, dist in zip(clean_closest_files, file_distances):
            if file_name != target_file:
                return dist
        return 0.0
    except Exception as e:
        raise RuntimeError(
            f"Error calculating min incorrect file distance for target '{target_file}': {e}"
        ) from e


def _make_row(
    data: list[dict[str, Any]], files_collection: chromadb.Collection
) -> pd.DataFrame:
    """Processes the test data queries and evaluates retrieval scores.

    Args:
        data: List of test cases, each containing user prompt and correct files.
        files_collection: The ChromaDB collection containing indexed codebase chunks.

    Returns:
        A DataFrame containing evaluation metrics for each test case.

    Raises:
        RuntimeError: If row processing fails.
    """
    try:
        rows_list = []

        for item in data:
            closest_files = find_closest_files(
                files_collection, item.get("user_prompt", "")
            )
            clean_closest_files = [_clean_filepath(f) for f in closest_files[0]]

            correct_files = item.get("correct_files", [])
            target_file = correct_files[0] if correct_files else ""

            max_correct_file = _max_correct_file(
                clean_closest_files,
                closest_files[1],
                target_file,
            )

            min_incorrect_file = _min_incorrect_file(
                clean_closest_files,
                closest_files[1],
                target_file,
            )

            new_row_data = {
                "Id": item.get("id"),
                "Target_file": target_file,
                "Max_correct_file": max_correct_file,
                "Min_incorrect_file": min_incorrect_file,
                "Delta": max_correct_file - min_incorrect_file,
            }
            rows_list.append(new_row_data)

        return pd.DataFrame(rows_list)
    except Exception as e:
        raise RuntimeError(
            f"Error occurred while processing evaluation rows: {e}"
        ) from e


def main() -> None:
    """Loads the test dataset, initializes index, runs evaluation, and saves outputs.

    Raises:
        RuntimeError: If the evaluation run fails.
    """
    try:
        with open("evals/synthetic_test_dataset_fixed.json", "r") as file:
            data = json.load(file)

        initialized_chroma_client = chroma_client_initialization(
            name="eval_codebase_rag"
        )
        splitter = code_aware_splitter()
        ignored_files = ignored_files_info()
        dir_path = os.getcwd()
        processed_files = file_info(dir_path, splitter, ignored_files)

        chromadb_batch_upsert(
            processed_files[0],
            processed_files[1],
            processed_files[2],
            initialized_chroma_client,
        )

        df = _make_row(data, initialized_chroma_client)
        valid_rows = df[df["Delta"] >= 0].mean(numeric_only=True)
        df.to_csv(f"{os.getcwd()}/evals/prompts_dataset.csv", index=False)
        print(valid_rows["Delta"])
    except Exception as e:
        raise RuntimeError(f"Evaluation process failed: {e}") from e


if __name__ == "__main__":
    main()
