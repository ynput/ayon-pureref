"""Increment workfile version plugin."""
import pyblish.api
from ayon_core.lib import version_up
from ayon_core.pipeline import registered_host


class IncrementWorkfileVersion(pyblish.api.ContextPlugin):
    """Save current file"""

    label = "Save current file"
    order = pyblish.api.ExtractorOrder - 0.49
    hosts = ["pureref"]
    families = ["workfile"]

    def process(self, context):
        path = context.data["currentFile"]
        host = registered_host()
        host.save_workfile(version_up(path))