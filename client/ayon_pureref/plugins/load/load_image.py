"""Loader plugin for loading still images into PureRef."""
from ayon_core.lib.transcoding import IMAGE_EXTENSIONS
from ayon_core.pipeline import load
from ayon_pureref.api.lib import open_pureref_file
from ayon_pureref.api.pipeline import containerise



class LoadImage(load.LoaderPlugin):
    """Load still image into Nuke"""

    product_base_types = {
        "render2d",
        "source",
        "plate",
        "render",
        "prerender",
        "review",
        "image",
    }
    product_types = product_base_types
    representations = {"*"}
    extensions = set(ext.lstrip(".") for ext in IMAGE_EXTENSIONS)

    settings_category = "pureref"

    label = "Load Image"
    order = -10
    icon = "image"
    color = "white"

    def load(self, context, name=None, namespace=None, data=None):
        filepath = self.filepath_from_context(context)
        open_pureref_file(filepath)
        return containerise(
            name=name,
            namespace=namespace,
            context=context,
            loader=self.__class__.__name__,
        )
