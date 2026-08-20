from __future__ import annotations

import os
import time

from .communication_server import CommunicationWrapper


def get_workdir() -> str:
    """Return the currently active work directory.

    Returns:
        str: The currently active work directory.
    """
    return os.environ["AYON_WORKDIR"]


def create_pur_file(filepath: str) -> None:
    """Create a PureRef file.

    Args:
        filepath (str): Path to the PureRef file to create.
    """
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            f.write("")


def execute_pureref_command(command: list, communicator=None) -> None:
    """Execute PureRef command.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    print(f"Executing command: {command}")
    return communicator.execute_command(command)


def open_pureref_file(
    filepath: str | None = None,
    communicator: CommunicationWrapper = None
) -> None:
    """Open a PureRef file.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    Args:
        filepath (str): Path to the PureRef file to open.
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.
    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    if filepath is None:
        return
    # load the new file in the same process, replacing the current one
    execute_pureref_command([f"{filepath}"], communicator)


def pre_pureref_exit(communicator: CommunicationWrapper = None) -> None:
    """Close previous workfile when opening/saving a workfile.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    Args:
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.
    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    command = ["-c", "exit"]
    execute_pureref_command(command, communicator)


def save_pureref_file(
    prev_filepath: str,
    file_path: str,
    communicator: CommunicationWrapper = None
) -> str:
    """Save the current PureRef file.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    Args:
        prev_filepath (str, optional): Path to the previous PureRef file to
            load before saving. If not provided, no previous file will be
            loaded.
        file_path (str): Path to save the PureRef file.
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.

    Returns:
        str: The path of the saved PureRef file.
    """
    # Create the file if it doesn't exist
    # This is to ensure that PureRef can save to
    # the specified path without issues.
    create_pur_file(file_path)
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    command = [
        "-c", f"load;{prev_filepath}",
        "-c", f"save;{file_path}",
        "-c", "exit",
    ]
    execute_pureref_command(command, communicator)
    # Wait a bit for the file to be saved before returning
    time.sleep(0.8)
    # asking PureRef to load back the latest file
    execute_pureref_command([f"{file_path}"], communicator)
    return file_path


def save_current_pureref_file(
    file_path: str,
    communicator: CommunicationWrapper = None
) -> None:
    """Save the current PureRef file.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    Args:
        file_path (str): Path to save the PureRef file.
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.

    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    command = [
        "-c", f"save;{file_path}",
    ]
    execute_pureref_command(command, communicator)


def export_pureref_image(
    file_path: str,
    communicator: CommunicationWrapper = None,
    **kwargs
) -> None:
    """Export the current PureRef file as an image.

    Note that this will *not* wait around for the PureRef command to run or
    for its completion. Nor will errors in the command be detected or raised.

    Args:
        file_path (str): Path to export the PureRef image.
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.
    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator
    command = [
        "-c", f"exportScene;{file_path}",
        f"{kwargs.get('resolutionWidth', 1920)};",
        f"{kwargs.get('resolutionHeight', 1080)};",
        "true;" if kwargs.get("canvas_background") else "false;",
        "true;" if kwargs.get("image_borders") else "false;",
        "true;" if kwargs.get("include_children") else "false;",
    ]
    execute_pureref_command(command, communicator)
