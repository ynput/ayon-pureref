"""Collect current file plugin."""
import pyblish.api
from ayon_core.pipeline import registered_host


class CollectCurrentFile(pyblish.api.ContextPlugin):
    """Collect the current file path and add it to the context data."""
    label = "Collect Current File"
    order = pyblish.api.CollectorOrder - 0.5
    hosts = ["pureref"]

    def process(self, context: pyblish.api.Context) -> None:
        host = registered_host()
        current_file = host.get_current_workfile()
        if not current_file:
            self.log.error("Scene is not saved. Please save the "
                           "scene with AYON workfile tools.")
        context.data["currentFile"] = current_file
