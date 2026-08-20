"""Set the CURRENT_PUR environment variable to the last Pureref workfile."""
import os

from ayon_applications import LaunchTypes, PreLaunchHook
from ayon_core.pipeline import tempdir
from ayon_pureref.api.lib import create_pur_file


class SetCurrentPurerefWorkfile(PreLaunchHook):
    """Get the last workfile path and set it to environment
    variable `CURRENT_PUR`.
    If the last workfile path is not set or the file does not exist, the
    environment variable will not be set.
    If user skips the last workfile, the environment variable will not be set.
    """  # ruff: ignore[missing-blank-line-after-summary]
    app_groups = {"pureref"}
    order = 12
    launch_types = {LaunchTypes.local}

    def execute(self):
        last_workfile = self.data.get("last_workfile_path")
        if (
            self.data.get("start_last_workfile")
            and last_workfile
            and os.path.exists(last_workfile)
        ):
            self.log.info("It is set to start last workfile on start.")
        else:
            staging_dir = tempdir.get_temp_dir(
                self.data["project_name"],
                use_local_temp=True
            )
            last_workfile = os.path.join(staging_dir, "untitled.pur")
            # create the untitled.pur file if it doesn't exist
            create_pur_file(last_workfile)
        # add the additonal commands to load the last workfile on startup
        self.launch_context.launch_args.append(last_workfile)
        # add the last workfile path to the launch arguments
        # during the load on startup so that AYON knows which
        # current workfile to load
        self.launch_context.env["CURRENT_PUR"] = last_workfile
