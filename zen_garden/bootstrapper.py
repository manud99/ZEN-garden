"""Helpers that bootstrap the optimization setup."""

from __future__ import annotations

import os


class ModelBootstrapper:
    """Builds the path map and element ordering for an optimization setup."""

    def __init__(self, analysis, system, input_data_checks, element_classes):
        self.analysis = analysis
        self.system = system
        self.input_data_checks = input_data_checks
        self.element_classes = element_classes
        self.path_data = self.analysis.dataset
        assert os.path.exists(
            self.path_data
        ), f"Folder for input data {self.analysis.dataset} does not exist!"
        self.input_data_checks.check_primary_folder_structure()
        self.paths = self._create_paths()
        self.element_list = self._build_element_list()

    def _create_paths(self):
        paths = {}
        for folder_name in next(os.walk(self.path_data))[1]:
            paths[folder_name] = {"folder": os.path.join(self.path_data, folder_name)}

        stack = [self.analysis.subsets]
        while stack:
            cur_dict = stack.pop()
            for set_name, subsets in cur_dict.items():
                path = paths[set_name]["folder"]
                if isinstance(subsets, dict):
                    stack.append(subsets)
                    self._add_folder_paths(paths, set_name, path, list(subsets.keys()))
                else:
                    self._add_folder_paths(paths, set_name, path, subsets)
                    for element in subsets:
                        if self.system[element]:
                            self._add_folder_paths(
                                paths, element, paths[element]["folder"]
                            )
        return paths

    def _add_folder_paths(self, paths, set_name, path, subsets=None):
        if subsets is None:
            subsets = []
        for element in next(os.walk(path))[1]:
            if element not in subsets:
                paths[set_name][element] = {"folder": os.path.join(path, element)}
                sub_path = os.path.join(path, element)
                for file in next(os.walk(sub_path))[2]:
                    paths[set_name][element][file] = os.path.join(sub_path, file)
                for parent_set in self._find_parent_set(
                    self.analysis.subsets, set_name
                ):
                    paths[parent_set][element] = paths[set_name][element]
            else:
                paths[element] = {"folder": os.path.join(path, element)}

    def _find_parent_set(self, dictionary, subset, path=None):
        if path is None:
            path = []
        for key, value in dictionary.items():
            current_path = path + [key]
            if subset in dictionary[key]:
                return current_path
            if isinstance(value, dict):
                result = self._find_parent_set(value, subset, current_path)
                if result:
                    return result
        return []

    def _build_element_list(self):
        element_classes = self.element_classes.keys()
        carrier_classes = [
            element_name
            for element_name in element_classes
            if "Carrier" in element_name
        ]
        technology_classes = [
            element_name
            for element_name in element_classes
            if "Technology" in element_name
        ]
        return technology_classes + carrier_classes
