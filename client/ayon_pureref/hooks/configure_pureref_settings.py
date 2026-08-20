"""Set the ini file for PureRef settings configuration."""
import os

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_pureref import PUREREF_ADDON_ROOT


class ConfigurePureRefSettings(PreLaunchHook):
    """Get the PureRef settings.ini file so that we can configure the settings
    in the silent mode.

    """  # ruff: ignore[missing-blank-line-after-summary]
    app_groups = {"pureref"}
    order = 11
    launch_types = {LaunchTypes.local}

    def execute(self) -> None:
        """Set the PureRef settings.ini file path to the launch arguments."""
        settings_ini_path = os.path.join(
            PUREREF_ADDON_ROOT, "api", "configuration", "PureRef.ini"
        )
        # ask the system to install the settings.ini file as the
        # default PureRef settings
        self.launch_context.launch_args.extend(["-S", settings_ini_path])
