"""File IO helpers for input data."""

from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import pandas as pd


class InputRepository:
    """Handles reading raw input files and attribute definitions."""

    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)

    def read_csv(self, input_file_name):
        input_file_name += ".csv"
        file_names = os.listdir(self.folder_path)
        if input_file_name not in file_names:
            return None

        df_input = pd.read_csv(
            os.path.join(self.folder_path, input_file_name),
            header=0,
            index_col=None,
        )
        if any("." in col for col in df_input.columns):
            raise AssertionError(
                f"The input data file {input_file_name} at "
                f"{self.folder_path} contains two identical header names."
            )
        return df_input

    def read_json(self, input_file_name):
        input_file_name += ".json"
        file_names = os.listdir(self.folder_path)
        if input_file_name not in file_names:
            return None
        with open(os.path.join(self.folder_path, input_file_name), "r") as file:
            return json.load(file)

    def load_attribute_file(self, filename="attributes"):
        if os.path.exists(self.folder_path / f"{filename}.json"):
            return self._load_attribute_file_json(filename=filename)
        if os.path.exists(self.folder_path / f"{filename}.csv"):
            raise NotImplementedError(
                f"The .csv format for attributes is deprecated "
                f"({filename} of {Path(self.folder_path).name}). Use .json instead."
            )
        raise FileNotFoundError(
            f"Attributes file does not exist for {Path(self.folder_path).name}"
        )

    def _load_attribute_file_json(self, filename):
        file_path = self.folder_path / f"{filename}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
        attribute_dict = {}
        if isinstance(data, list):
            warnings.warn(
                "The list format in attributes.json [{...}] is deprecated. "
                "Use a dict format instead {...}.",
                DeprecationWarning,
                stacklevel=2,
            )
            for item in data:
                for k, v in item.items():
                    if isinstance(v, list):
                        attribute_dict[k] = {sk: sv for d in v for sk, sv in d.items()}
                    else:
                        attribute_dict[k] = v
        else:
            for k, v in data.items():
                if isinstance(v, list):
                    attribute_dict[k] = {sk: sv for d in v for sk, sv in d.items()}
                else:
                    attribute_dict[k] = v
        return attribute_dict
