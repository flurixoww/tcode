import json
import os

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
    if ".py" in path_string:
        path_string = path_string.split(".py")[0] + ".py"
    return os.path.basename(path_string)


def _dataframe_init() -> pd.DataFrame:
    main_df = pd.DataFrame(
        columns=[
            "Id",
            "Target_file",
            "Max_correct_file",
            "Min_incorrect_file",
            "Delta",
        ]
    )
    return main_df


def _max_correct_file(
    clean_closest_files: list, file_distances: list, target_file: str
) -> float:
    file_distance = 0
    for file_id in range(len(clean_closest_files)):
        temp_file = 0
        if (
            clean_closest_files[file_id] == target_file
            and file_distances[file_id] > temp_file
        ):
            temp_file = file_distances[file_id]
            file_distance = file_distances[file_id]
    return file_distance


def _min_incorrect_file(
    clean_closest_files: list, file_distnaces: list, target_file: str
) -> float:
    for file_id in range(len(clean_closest_files)):
        if clean_closest_files[file_id] != target_file:
            file_distnace = file_distnaces[file_id]
            return file_distnace
    return 0.0


def _make_row(data, chroma_client) -> pd.DataFrame:
    rows_list = []

    for file in range(len(data)):
        closest_files = find_closest_files(chroma_client, data[file].get("user_prompt"))
        clean_closest_files = []
        for close_file in closest_files[0]:
            clean_closest_files.append(_clean_filepath(close_file))

        max_correct_file = _max_correct_file(
            clean_closest_files,
            closest_files[1],
            data[file].get("correct_files")[0],
        )

        min_incorrect_file = _min_incorrect_file(
            clean_closest_files,
            closest_files[1],
            data[file].get("correct_files")[0],
        )
        new_row_data = {
            "Id": data[file].get("id"),
            "Target_file": data[file].get("correct_files")[0],
            "Max_correct_file": max_correct_file,
            "Min_incorrect_file": min_incorrect_file,
            "Delta": max_correct_file - min_incorrect_file,
        }
        rows_list.append(new_row_data)
    df = pd.DataFrame(rows_list)
    return df


def main() -> None:
    with open("evals/synthetic_test_dataset_fixed.json", "r") as file:
        data = json.load(file)
    initialized_chroma_client = chroma_client_initialization(name="eval_codebase_rag")
    splitter = code_aware_splitter()
    ignored_files = ignored_files_info()
    dir_path = "/Users/flurixoww/Documents/Projects/tcode"
    processed_files = file_info(dir_path, splitter, ignored_files)
    chromadb_batch_upsert(
        processed_files[0],
        processed_files[1],
        processed_files[2],
        initialized_chroma_client,
    )
    for file in data:
        user_prompt = file.get("user_prompt")
        closest_files = find_closest_files(initialized_chroma_client, user_prompt)
        print(closest_files[0])
        print(closest_files[1])
        print(file.get("id"))
        print(file.get("correct_files"))


def test() -> None:
    with open("evals/synthetic_test_dataset_fixed.json", "r") as file:
        data = json.load(file)

    initialized_chroma_client = chroma_client_initialization(name="eval_codebase_rag")
    splitter = code_aware_splitter()
    ignored_files = ignored_files_info()
    dir_path = "/Users/flurixoww/Documents/Projects/tcode"
    processed_files = file_info(dir_path, splitter, ignored_files)
    chromadb_batch_upsert(
        processed_files[0],
        processed_files[1],
        processed_files[2],
        initialized_chroma_client,
    )
    df = _make_row(data, initialized_chroma_client)
    valid_rows = df[df["Delta"] >= 0].mean(numeric_only=True)
    print(valid_rows["Delta"])


if __name__ == "__main__":
    test()
