"""Creator plugin for image."""
from ayon_pureref.api import plugin


class CreateImage(plugin.PureRefCreator):
    """Creator plugin for Image."""
    identifier = "io.ayon.creators.pureref.image"
    label = "Image"
    product_base_type = "image"
    product_type = product_base_type
    icon = "picture-o"
