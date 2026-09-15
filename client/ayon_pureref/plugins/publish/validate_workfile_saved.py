"""Validate that workfile was saved."""
import pyblish.api
from ayon_core.pipeline import PublishValidationError


class ValidateWorkfileSaved(pyblish.api.ContextPlugin):
    """Validate that workfile was saved."""

    order = pyblish.api.ValidatorOrder
    families = ["workfile"]
    hosts = ["pureref"]
    label = "Validate Workfile is saved"

    def process(self, context):
        if "untitled.pur" in context.data["currentFile"]:
            raise PublishValidationError(
                "Workfile is not saved.", title=self.label)
