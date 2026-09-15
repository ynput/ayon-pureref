"""Loader plugin for loading workfiles into PureRef."""
import os
from ayon_core.pipeline import load
from ayon_core.pipeline import registered_host


class WorkfileLoader(load.LoaderPlugin):
    """PureRef Workfile Loader."""

    product_base_types = {"workfile"}
    product_types = product_base_types
    representations = {"*"}
    extensions = {"pur"}
    order = -9
    icon = "code-fork"
    color = "white"
    label = "Load Workfile"

    def load(self, context, name=None, namespace=None, data=None):
        file_path = os.path.normpath(
            self.filepath_from_context(context)
        )
        if not os.path.exists(file_path):
            raise FileExistsError("The loaded file not found.")

        host = registered_host()
        host.open_workfile(file_path)
