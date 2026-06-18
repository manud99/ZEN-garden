from linopy import Model as LinopyModel


class ZenModel(LinopyModel):
    """Wrapper around linopy.Model. Only a dummy so far..."""

    sets: list[str]
