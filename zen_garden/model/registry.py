"""Explicit registry for model element classes."""

from __future__ import annotations

from collections import OrderedDict
from typing import TypeVar

ElementClassT = TypeVar("ElementClassT")

ELEMENT_CLASS_REGISTRY: "OrderedDict[str, type]" = OrderedDict()


def register_element_class(cls: ElementClassT) -> ElementClassT:
    """Register a model element class explicitly."""
    ELEMENT_CLASS_REGISTRY[cls.__name__] = cls
    return cls


def get_registered_element_classes() -> dict[str, type]:
    """Return a copy of the registered element classes."""
    return dict(ELEMENT_CLASS_REGISTRY)
