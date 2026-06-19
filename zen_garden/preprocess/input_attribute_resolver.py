"""Attribute resolution helpers for input data."""

from __future__ import annotations

import warnings


class InputAttributeResolver:
    """Resolves attribute defaults, scenario overrides, and deprecations."""

    def __init__(self, element, context, repository, base_attribute_dict):
        self.element = element
        self.context = context
        self.repository = repository
        self.base_attribute_dict = base_attribute_dict

    def get_attribute_dict(self, attribute_name):
        if self.context is not None:
            filename, factor = self.context.scenario_dict.get_default(
                self.element.name, attribute_name
            )
        else:
            filename = "attributes"
            factor = 1
        if filename != "attributes":
            attribute_dict = self.repository.load_attribute_file(filename)
        else:
            attribute_dict = self.base_attribute_dict
        return attribute_dict, factor

    def extract_attribute_value(self, attribute_name, attribute_dict):
        if attribute_name not in attribute_dict:
            parameter_change_log = getattr(self.context, "parameter_change_log", None)
            if parameter_change_log is None:
                raise AttributeError(
                    f"Attribute {attribute_name} does not exist in input data "
                    f"of {self.element.name}"
                )

            if attribute_name in parameter_change_log:
                if isinstance(parameter_change_log[attribute_name], dict):
                    missing_attribute = parameter_change_log[attribute_name]

                    if missing_attribute["default_value"] not in [0, 1, "inf"]:
                        raise AttributeError(
                            f"Default value of attribute {attribute_name} must "
                            f"be 0 , 1, or 'inf' but is "
                            f"{missing_attribute['default_value']}"
                        )

                    attribute_dict[attribute_name] = {
                        "default_value": missing_attribute["default_value"],
                        "unit": attribute_dict[missing_attribute["unit"]]["unit"],
                    }

                    warnings.warn(
                        f"\nAttribute {attribute_name} is not yet included in "
                        f"your model. Automatic assign default_value:"
                        f"{attribute_dict[attribute_name]['default_value']}, "
                        f"unit: {attribute_dict[attribute_name]['unit']}\n",
                        DeprecationWarning,
                        stacklevel=2,
                    )
                else:
                    old_name = parameter_change_log[attribute_name]
                    attribute_dict[attribute_name] = attribute_dict.pop(old_name)

                    warnings.warn(
                        f"Attribute {old_name} is now called {attribute_name}",
                        DeprecationWarning,
                        stacklevel=2,
                    )
            else:
                raise AttributeError(
                    f"Attribute {attribute_name} does not exist in input data "
                    f"of {self.element.name}"
                )
        try:
            attribute_value = float(attribute_dict[attribute_name]["default_value"])
            attribute_unit = attribute_dict[attribute_name]["unit"]
        except ValueError:
            attribute_value = attribute_dict[attribute_name]["default_value"]
            attribute_unit = attribute_dict[attribute_name]["unit"]
        except (TypeError, KeyError):
            if "default_value" in attribute_dict[attribute_name]:
                attribute_value = attribute_dict[attribute_name]["default_value"]
            else:
                attribute_value = attribute_dict[attribute_name]
            attribute_unit = None
        return attribute_value, attribute_unit
