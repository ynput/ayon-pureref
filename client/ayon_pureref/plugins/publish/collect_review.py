"""Collect review plugin."""
import pyblish.api


class CollectReview(pyblish.api.InstancePlugin):
    """Collect Review and adds review as parts of the
    families if there is one in the instance data"""
    label = "Collect Review"
    order = pyblish.api.CollectorOrder - 0.4
    hosts = ["pureref"]

    def process(self, instance: pyblish.api.Instance) -> None:
        creator_attributes = instance.data["creator_attributes"]
        if creator_attributes.get("review", False):
            instance.data["families"].append("review")
