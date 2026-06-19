"""Read-only model context shared across setup, model, and data loading."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from zen_garden.default_config import Analysis, Solver, System


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(val) for key, val in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


@dataclass(frozen=True, slots=True)
class ModelContext:
    """Immutable bundle of model state shared across layers."""

    analysis: Analysis
    system: System
    solver: Solver
    paths: Mapping[str, Any]
    path_data: str
    element_classes: Mapping[str, type]
    scenario_dict: Any = None
    input_data_checks: Any = None
    energy_system: Any = None
    parameter_change_log: Any = None
    year_specific_ts: dict[int, dict[tuple[str, str], Any]] | None = None

    @classmethod
    def from_setup(
        cls,
        analysis: Analysis,
        system: System,
        solver: Solver,
        paths: Mapping[str, Any],
        path_data: str,
        element_classes: Mapping[str, type],
        input_data_checks: Any = None,
        scenario_dict: Any = None,
        energy_system: Any = None,
        parameter_change_log: Any = None,
        year_specific_ts: dict[int, dict[tuple[str, str], Any]] | None = None,
    ) -> "ModelContext":
        return cls(
            analysis=analysis,
            system=system,
            solver=solver,
            paths=_freeze(dict(paths)),
            path_data=path_data,
            element_classes=dict(element_classes),
            scenario_dict=scenario_dict,
            input_data_checks=input_data_checks,
            energy_system=energy_system,
            parameter_change_log=parameter_change_log,
            year_specific_ts=year_specific_ts if year_specific_ts is not None else {},
        )

    def with_updates(self, **kwargs: Any) -> "ModelContext":
        return replace(self, **kwargs)

    def resolve_class_label(self, class_label: str) -> str:
        if class_label in self.paths:
            return class_label
        stack = [self.analysis.subsets]
        while stack:
            current = stack.pop()
            for set_name, subsets in current.items():
                if isinstance(subsets, dict):
                    if class_label in subsets:
                        return set_name
                    stack.append(subsets)
                elif isinstance(subsets, list) and class_label in subsets:
                    return set_name
        return class_label

    def get_input_folder(self, class_label: str, element_name: str) -> Path:
        resolved_class_label = self.resolve_class_label(class_label)
        return Path(self.paths[resolved_class_label][element_name]["folder"])
