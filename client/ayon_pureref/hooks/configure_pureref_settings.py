"""Set the ini file for PureRef settings configuration."""

from ayon_applications import LaunchTypes, PreLaunchHook


class ConfigurePureRefSettings(PreLaunchHook):
    """Get the PureRef settings.ini file so that we can configure the settings
    in the silent mode.

    """  # ruff: ignore[missing-blank-line-after-summary]
    app_groups = {"pureref"}
    order = 11
    launch_types = {LaunchTypes.local}

    def execute(self) -> None:
        """Set up the PureRef settings.ini parameters to the launch arguments.
        """
        # ask the system to install the settings.ini file as the
        # default PureRef settings
        self.launch_context.launch_args.extend(
            ["-S", "OpenFilesIn=CurrentWindow",
             "-S", "Unsaved_Scene_Behavior=Discard",
             "-S", "Always_On_Top=true",
             "-S", "PeriodicSave=true"
             ]
        )
