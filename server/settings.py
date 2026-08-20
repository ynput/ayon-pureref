"""Settings for the PureRef addon."""
from ayon_server.settings import BaseSettingsModel, SettingsField


def image_format_enum() -> list[dict[str, str]]:
    """Return enumerator for image output formats."""
    return [
        {"label": "bmp", "value": "bmp"},
        {"label": "jpg", "value": "jpg"},
        {"label": "png", "value": "png"},
    ]


class ExtractImageSettings(BaseSettingsModel):
    """Settings for the ExtractImage plugin."""
    extension: str = SettingsField(
        enum_resolver=image_format_enum,
        title="Image extension"
    )
    resolution_width: int = SettingsField(title="Resolution width")
    resolution_height: int = SettingsField(title="Resolution height")
    canvas_background: bool = SettingsField(title="Canvas background")
    image_borders: bool = SettingsField(title="Image borders")
    include_children: bool = SettingsField(title="Include children")


class PublisherModel(BaseSettingsModel):
    ExtractImage: ExtractImageSettings = SettingsField(
        default_factory=ExtractImageSettings,
        title="Extract Image"
    )


class PureRefSettings(BaseSettingsModel):
    """Settings for the addon."""
    publish: PublisherModel = SettingsField(
        default_factory=PublisherModel,
        title="Publish"
    )


DEFAULT_PUREREF_VALUES = {
    "publish": {
        "ExtractImage": {
            "extension": "png",
            "resolution_width": 1920,
            "resolution_height": 1080,
            "canvas_background": False,
            "image_borders": False,
            "include_children": False
        }
    }
}
