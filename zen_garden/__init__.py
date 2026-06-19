from . import wrapper
from .model.registry import get_registered_element_classes
from .optimization_setup import OptimizationSetup
from .postprocess.comparisons import (
    compare_configs,
    compare_dicts,
    compare_model_values,
)
from .postprocess.results.results import Results
from .runner import run
from .utils import download_example_dataset

__all__ = [
    "run",
    "Results",
    "download_example_dataset",
    "compare_model_value",
    "compare_configs",
    "compare_model_values",
    "compare_dicts",
    "wrapper",
]

OptimizationSetup.dict_element_classes.update(get_registered_element_classes())
