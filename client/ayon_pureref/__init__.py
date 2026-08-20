"""AYON PureRef client package."""
from .addon import PUREREF_ADDON_ROOT, PureRefAddon, get_launch_script_path
from .version import __version__

__all__ = (
    "PUREREF_ADDON_ROOT",
    "PureRefAddon",
    "__version__",
    "get_launch_script_path",
)
