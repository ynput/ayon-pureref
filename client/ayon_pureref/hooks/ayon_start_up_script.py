"""Pre-launch to force PureRef startup script."""
from ayon_pureref import get_launch_script_path
from ayon_core.lib import get_ayon_launcher_args
from ayon_applications import PreLaunchHook, LaunchTypes


class PureRefStartupScript(PreLaunchHook):
    """Inject AYON plugins to PureRef.

    Note that this works in combination whit PureRef startup script that
    is creating the environment variable for the AYON Plugin

    Hook `GlobalHostDataHook` must be executed before this hook.
    """
    app_groups = {"pureref"}
    order = 10
    launch_types = {LaunchTypes.local}

    def execute(self):
        executable_path = self.launch_context.launch_args.pop(0)
        self.launch_context.env["PUREREF_EXE"] = executable_path
        # Pop rest of launch arguments - There should not be other arguments!
        remainders = []
        new_launch_args = get_ayon_launcher_args(
            "run", get_launch_script_path(), executable_path
        )
        # Append as whole list as these arguments should not be separated
        self.launch_context.launch_args.append(new_launch_args)

        if remainders:
            self.log.warning((
                "There are unexpected launch arguments in PureRef launch. {}"
            ).format(str(remainders)))
            self.launch_context.launch_args.extend(remainders)
