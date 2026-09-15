"""Plugin for extracting image from PureRef."""
import os

import pyblish.api
from ayon_core.lib import BoolDef, NumberDef, UISeparatorDef, UILabelDef
from ayon_core.pipeline import publish
from ayon_core.pipeline.publish import AYONPyblishPluginMixin
from ayon_pureref.api.lib import export_pureref_image


class ExtractImage(publish.Extractor,
                   AYONPyblishPluginMixin):
    """Extract Image(png, jpg, bmp) from PureRef."""

    order = pyblish.api.ExtractorOrder - 0.05
    label = "Extract Image"
    hosts = ["pureref"]
    families = ["image"]

    settings_category = "pureref"
    # settings
    extension = "png"
    resolution_width = 1920
    resolution_height = 1080
    canvas_background = False
    image_borders = False
    include_children = False

    def process(self, instance: pyblish.api.Instance) -> None:
        staging_dir = self.staging_dir(instance)
        filename = f"{instance.name}.{self.extension}"
        filepath = os.path.join(staging_dir, filename)
        attr_values = self.get_attr_values_from_data(instance.data)
        export_pureref_image(
            instance.context.data["currentFile"],
            filepath,
            resolutionWidth=attr_values["resolutionWidth"],
            resolutionHeight=attr_values["resolutionHeight"],
            canvasBackground=attr_values.get("canvasBackground", False),
            imageBorders=attr_values.get("imageBorders", False),
            includeChildren=attr_values.get("includeChildren", False),
        )

        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
        "name": self.extension,
        "ext": self.extension,
        "files": filename,
        "stagingDir": staging_dir,
        }

        creator_attributes = instance.data["creator_attributes"]
        if creator_attributes.get("review", False):
            instance.data["families"].append("review")
            representation["tags"] = ["review"]

        instance.data["representations"].append(representation)
        self.log.info(
            f"Extracted instance '{instance.name}' to: {filepath}"
        )

    @classmethod
    def get_attribute_defs(cls) -> list[dict]:
        """Get the attribute definitions for the plugin.

        Returns:
            list[dict]: The attribute definitions for the plugin.
        """
        return [
            UISeparatorDef("sep_extract_image_options"),
            UILabelDef("Extract Image Options"),
            NumberDef("resolutionWidth",
                      label="Resolution width",
                      decimals=0,
                      minimum=0,
                      default=cls.resolution_width
            ),
            NumberDef("resolutionHeight",
                      label="Resolution height",
                      decimals=0,
                      minimum=0,
                      default=cls.resolution_height
            ),
            BoolDef("canvasBackground",
                     label="Canvas background",
                     default=cls.canvas_background
            ),
            BoolDef("imageBorders",
                     label="Image borders",
                    default=cls.image_borders
            ),
            BoolDef("includeChildren",
                     label="Include children",
                    default=cls.include_children
            ),
        ]
