"""Increment workfile version plugin."""
import os

import pyblish.api
from ayon_core.host.interfaces import SaveWorkfileOptionalData
from ayon_core.pipeline.workfile import save_next_version
from ayon_pureref.api.lib import save_file_with_hotkey


class IncrementWorkfileVersion(pyblish.api.ContextPlugin):
    """Save current file"""

    label = "Save current file"
    order = pyblish.api.ExtractorOrder - 0.49
    hosts = ["pureref"]
    families = ["workfile"]

    def process(self, context):
        path = context.data["currentFile"]
        current_filename = os.path.basename(path)
        save_file_with_hotkey()
        save_next_version(
            description=(
                f"Incremented by publishing from {current_filename}"
            ),
            # Optimize the save by reducing needed queries for context
            prepared_data=SaveWorkfileOptionalData(
                project_entity=context.data["projectEntity"],
                project_settings=context.data["project_settings"],
                anatomy=context.data["anatomy"],
            )
        )
