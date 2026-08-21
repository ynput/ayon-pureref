"""Collect workfile plugin."""
import json
import os

import pyblish.api


class CollectWorkfile(pyblish.api.InstancePlugin):
    """Collect the current workfile path and add it to the instance data."""
    label = "Collect Workfile"
    order = pyblish.api.CollectorOrder - 0.4
    hosts = ["pureref"]
    families = ["workfile"]

    def process(self, instance: pyblish.api.Instance) -> None:
        context = instance.context
        current_file = context.data["currentFile"]
        product_type = instance.data.get("productType")
        if not product_type:
            product_type = instance.data["productBaseType"]

        self.log.info(
            f"Workfile path used for product type: {current_file}"
        )

        dirpath, filename = os.path.split(current_file)
        _basename, ext = os.path.splitext(filename)

        instance.data["representations"].append({
            "name": ext.lstrip("."),
            "ext": ext.lstrip("."),
            "files": filename,
            "stagingDir": dirpath
        })
        data = json.dumps(instance.data, indent=4)
        self.log.info(f"Collected workfile instance: {data}")
