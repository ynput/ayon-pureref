"""Useful functions to communicate with PureRef."""
from __future__ import annotations

import os
import time

from ayon_core.pipeline import PublishError

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


def export_pureref_image(
    current_workfile: str,
    file_path: str,
    communicator: CommunicationWrapper = None,
    **kwargs
) -> None:
    """Export the current PureRef file as an image.

    Args:
        current_workfile (str): Path to the current PureRef file.
        file_path (str): Path to save the exported image.
        communicator (CommunicationWrapper, optional): The communicator to use.
            If not provided, the default communicator will be used.
        **kwargs: Additional keyword arguments to pass to the export command.
            Supported arguments:
                - resolutionWidth (int): The width of the exported image.
                - resolutionHeight (int): The height of the exported image.
                - canvas_background (bool): Whether to include the canvas
                    background in the exported image.
                - image_borders (bool): Whether to include image borders in the
                    exported image.
                - include_children (bool): Whether to include children in the
                    exported image.
                - timeout (int): The maximum time to wait for the export to
                    complete, in seconds. Default is 60 seconds.

    Raises:
        PublishError: If the export times out and the image file is not
            created.
    """
    if communicator is None:
        communicator = CommunicationWrapper.communicator

    # Build the exportScene command in one string
    export_cmd = (
        f"exportScene;{file_path};"
        f"{kwargs.get('resolutionWidth', 1920)};"
        f"{kwargs.get('resolutionHeight', 1080)};"
        f"{'true' if kwargs.get('canvas_background') else 'false'};"
        f"{'true' if kwargs.get('image_borders') else 'false'};"
        f"{'true' if kwargs.get('include_children') else 'false'}"
    )

    command = [
        "-c", f"load;{current_workfile}",
        "-c", export_cmd,
        "-c", "exit",
    ]

    execute_pureref_command(command, communicator)

    # Wait until the image file exists (with timeout)
    timeout = kwargs.get("timeout", 60)  # default 60s
    start = time.time()
    while True:
        if os.path.isfile(file_path):
            break
        if time.time() - start > timeout:
            raise PublishError(f"Export timed out: {file_path} not created")
        time.sleep(2)
