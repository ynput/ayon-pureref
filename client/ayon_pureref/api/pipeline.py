"""Pipeline tools for AYON PureRef integration."""
from __future__ import annotations
import ast
import json
import logging
import os
import shutil
from typing import Union

import pyblish.api
from ayon_core.host import HostBase, ILoadHost, IPublishHost, IWorkfileHost
from ayon_core.lib import register_event_callback
from ayon_core.pipeline import (
    AYON_CONTAINER_ID,
    register_creator_plugin_path,
    register_loader_plugin_path,
    registered_host,
)
from ayon_core.pipeline.context_tools import get_global_context

from ayon_pureref import PUREREF_ADDON_ROOT

from .lib import get_workdir, open_pureref_file, save_pureref_file

METADATA_SECTION = "ayon"
PUREREF_SECTION_NAME_CONTEXT = "context"
PUREREF_METADATA_CREATE_CONTEXT = "create_context"
PUREREF_SECTION_NAME_INSTANCES = "instances"
PUREREF_SECTION_NAME_CONTAINERS = "containers"


log = logging.getLogger("ayon.hosts.pureref")


class PureRefHost(HostBase, IWorkfileHost, ILoadHost, IPublishHost):
    name = "pureref"

    @staticmethod
    def show_tools_dialog():
        """Show tools dialog with actions leading to show other tools."""
        show_tools_dialog()

    def install(self):

        plugins_dir = os.path.join(PUREREF_ADDON_ROOT, "plugins")
        publish_dir = os.path.join(plugins_dir, "publish")
        load_dir = os.path.join(plugins_dir, "load")
        create_dir = os.path.join(plugins_dir, "create")

        pyblish.api.register_host("pureref")
        pyblish.api.register_plugin_path(publish_dir)
        register_loader_plugin_path(load_dir)
        register_creator_plugin_path(create_dir)

        register_event_callback(
            "application.launched", self.initial_app_launch
        )
        register_event_callback("application.exit", self.application_exit)

    def get_current_project_name(self) -> Union[str, None]:
        """Get current project name from the current context.

        Returns:
            Union[str, None]: Current project name.
        """
        return self.get_current_context().get("project_name")

    def get_current_folder_path(self) -> Union[str, None]:
        """Get current folder path from the current context.

        Returns:
            Union[str, None]: Current folder path.
        """
        return self.get_current_context().get("folder_path")

    def get_current_task_name(self) -> Union[str, None]:
        """Get current task name from the current context.

        Returns:
            Union[str, None]: Current task name.
        """
        return self.get_current_context().get("task_name")

    def get_current_context(self) -> Union[dict, None]:
        """Get current context data from the current workfile.

        Returns:
            Union[dict, None]: Context data
        """
        context = get_current_workfile_context()
        if not context:
            return get_global_context()

        return context

    def get_current_workfile(self) -> Union[str, None]:  # ruff: ignore[no-self-use]
        """Get current workfile path.

        Returns:
            Union[str, None]: current workfile path.
            If no workfile is opened, returns None.
        """
        if os.getenv("CURRENT_PUR"):
            return os.environ["CURRENT_PUR"]
        return None

    def workfile_has_unsaved_changes(self) -> bool:  # ruff: ignore[no-self-use]
        # No command to check for unsaved changes in PureRef,
        # so we assume there are no unsaved changes.
        return False

    def get_workfile_extensions(self) -> list[str]:  # ruff: ignore[no-self-use]
        return [".pur"]

    def open_workfile(self, filepath):
        """Open current workfile with AYON Plugins."""
        open_pureref_file(filepath)
        os.environ["CURRENT_PUR"] = filepath
        return filepath

    def save_workfile(self, filepath=None):
        prev_filepath = self.get_current_workfile()
        filepath = save_pureref_file(prev_filepath, filepath)
        print(f"Saving pur file: {filepath}")
        copy_ayon_data(filepath)
        os.environ["CURRENT_PUR"] = filepath
        return filepath

    def list_instances(self):
        """Get all AYON instances."""
        # Figure out how to deal with this
        return get_instance_workfile_metadata()

    def write_instances(self, data):
        """Write all AYON instances"""
        return write_workfile_metadata(PUREREF_SECTION_NAME_INSTANCES, data)

    def get_containers(self):
        """Get the data of the containers

        Returns:
            list: the list which stores the data of the containers
        """
        return get_containers()

    def initial_app_launch(self) -> None:  # ruff: ignore[no-self-use]
        """Triggers on launch of the communication server for PureRef.

        Usually this aligns roughly with the start of PureRef.
        """
        context = get_global_context()
        save_current_workfile_context(context)

    def application_exit(self) -> None:  # ruff: ignore[no-self-use]
        """Event action when the application exit"""
        remove_tmp_data()

    def update_context_data(self, data, changes):
        return write_workfile_metadata(PUREREF_METADATA_CREATE_CONTEXT, data)

    def get_context_data(self):
        return get_load_context_metadata(PUREREF_METADATA_CREATE_CONTEXT)


def containerise(
        name: str,
        context: dict,
        namespace: str = "",
        loader: str | None = None,
        containers: list | None = None
    ) -> dict:
    """Imprint a loaded container with metadata.

    Containerisation enables a tracking of version, author and origin
    for loaded assets.

    Args:
        name (str): name
        context (dict): context
        namespace (str, optional): namespace. Defaults to "".
        loader (str, optional): name of the loader. Defaults to None.
        containers (list, optional): existing containers. Defaults to None.

    Returns:
        dict: data
    """
    data = {
        "schema": "ayon:container-2.0",
        "id": AYON_CONTAINER_ID,
        "name": name,
        "namespace": namespace,
        "loader": str(loader),
        "representation": str(context["representation"]["id"]),
    }
    if containers is None:
        containers = get_containers()

    containers.append(data)

    write_load_metadata(containers)
    return data


def save_current_workfile_context(context: dict) -> None:
    """Save current workfile context data to`.pureref_metadata/{workfile}/key`.

    This persists the current in-memory context to be set for a specific
    workfile on disk. Usually used on save to persist the local sessions'
    workfile context on save.

    The context data includes things like the project name, folder path,
    etc.

    Args:
        context (dict): context data

    """
    return write_context_metadata(PUREREF_SECTION_NAME_CONTEXT, context)


def write_context_metadata(metadata_key: str, context: dict) -> None:
    """Write context data into the related json
    which stores in .pureref_metadata/key folder
    in the project work directory.
    The context data includes the project name,
    folder path and task name.

    Args:
        metadata_key (str): metadata key
        context (dict): context data
    """
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata", metadata_key).replace(
            "\\", "/"
        )
    os.makedirs(json_dir, exist_ok=True)
    json_file = f"{json_dir}/{metadata_key}.json"
    if os.path.exists(json_file):
        with open(json_file, "r") as file:
            value = json.load(file)
            if value == context:
                return
    with open(json_file, "w") as file:
        value = json.dumps(context)
        file.write(value)
        file.close()


def write_workfile_metadata(metadata_key: str, data=None) -> None:
    """Function to write workfile metadata(such as creator's context data
    and instance data) in .pureref_metadata/{workfile}/{metadata_key} folder
    This persists the current in-memory instance/creator's context data
    to be set for a specific workfile on disk. Usually used on save to
    persist updating instance data and context data used in publisher.

    Args:
        metadata_key (str): metadata key
        data (list, optional): metadata. Defaults to None.
    """
    if data is None:
        data = []
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, metadata_key).replace(
            "\\", "/"
        )
    os.makedirs(json_dir, exist_ok=True)
    with open(f"{json_dir}/{metadata_key}.json", "w") as file:
        value = json.dumps(data)
        file.write(value)
        file.close()


def get_current_workfile_context() -> dict:
    """Function to get the current context data from the related
    json file in .pureref_metadata/context folder

    The current context data includes thing like project name,
    folder path and task name.

    Returns:
        dict: current context data
    """
    return get_load_context_metadata()


def get_containers():
    """Function to get the container data

    Returns:
        list: list of container data
    """
    output = get_load_workfile_metadata(PUREREF_SECTION_NAME_CONTAINERS)
    if output:
        for item in output:
            if "objectName" not in item and "name" in item:
                members = item["name"]
                if isinstance(members, list):
                    members = "|".join([str(member) for member in members])
                item["objectName"] = members

    return output


def write_load_metadata(data):
    """Write/Edit the container data into the related json file
    ("{subset_name}.json")
    which stores in .pureref_metadata/{workfile}/containers folder.
    This persists the current in-memory containers data
    to be set for updating and switching assets in scene inventory.

    Args:
        metadata_key (str): metadata key for container
        data (list): list of container data
    """
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    name = next((d["name"] for d in data), None)
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, PUREREF_SECTION_NAME_CONTAINERS).replace(
            "\\", "/"
        )
    os.makedirs(json_dir, exist_ok=True)
    json_file = f"{json_dir}/{name}.json"
    if os.path.exists(json_file):
        with open(json_file, "w"):
            pass

    with open(json_file, "w") as file:
        value = json.dumps(data)
        file.write(value)
        file.close()


def copy_ayon_data(filepath):
    """Copy any ayon-related data(
        such as instances, create-context, cotnainers)
        from the previous workfile to the new one
        when incrementing and saving workfile.

    Args:
        filepath (str): the workfile path to be saved
    """
    filename = os.path.splitext(os.path.basename(filepath))[0].strip()
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    for name in [PUREREF_METADATA_CREATE_CONTEXT,
                 PUREREF_SECTION_NAME_INSTANCES,
                 PUREREF_SECTION_NAME_CONTAINERS]:
        src_json_dir = os.path.join(
            work_dir, ".pureref_metadata", current_file, name).replace(
                "\\", "/"
            )
        if not os.path.exists(src_json_dir):
            continue
        dst_json_dir = os.path.join(
            work_dir, ".pureref_metadata", filename, name).replace(
                "\\", "/"
            )
        os.makedirs(dst_json_dir, exist_ok=True)
        all_fname_list = [jfile for jfile in os.listdir(src_json_dir)
                        if jfile.endswith("json")]
        if all_fname_list:
            for fname in all_fname_list:
                src_json = f"{src_json_dir}/{fname}"
                dst_json = f"{dst_json_dir}/{fname}"
                shutil.copy(src_json, dst_json)


def get_load_context_metadata(
        context_name: str = PUREREF_SECTION_NAME_CONTEXT) -> dict:
    """Get the context data from the related json file
    ("context.json") which stores in .pureref_metadata/context
    folder in the project work directory.

    The context data includes the project name, folder path and
    task name.

    Args:
        context_name (str): name of the context

    Returns:
        dict: context data
    """  # ruff: ignore[missing-blank-line-after-summary]
    file_content = {}
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata", context_name).replace(
            "\\", "/"
        )
    if not os.path.exists(json_dir):
        return file_content
    file_list = os.listdir(json_dir)
    if not file_list:
        return file_content
    for file in file_list:
        with open(f"{json_dir}/{file}", "r") as data:
            content = ast.literal_eval(str(data.read().strip()))
            file_content.update(content)
            data.close()
    return file_content


def get_load_workfile_metadata(metadata_key: str) -> list[dict]:
    """Get to load the workfile json metadata(such as
    creator's context data and container data) which stores in
    .pureref_metadata/{workfile}/{metadata_key} folder in the project
    work directory.
    It mainly supports to the metadata_key below:
    PUREREF_METADATA_CREATE_CONTEXT: loading create_context.json where
        stores the data with publish_attributes(e.g. whether the
        optional validator is enabled.)
    PUREREF_SECTION_NAME_CONTAINERS: loading {subset_name}.json where
        includes all the loaded asset data to the PureRef scene.

    Args:
        metadata_key (str): name of the metadata key

    Returns:
        list: list of metadata(create-context data or container data)
    """
    file_content = []
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, metadata_key).replace(
            "\\", "/"
        )
    if not os.path.exists(json_dir):
        return file_content
    file_list = os.listdir(json_dir)
    if not file_list:
        return file_content
    for file in file_list:
        with open(f"{json_dir}/{file}", "r") as data:
            content = json.load(data)
            file_content.extend(content)
            data.close()
    return file_content


def imprint(container: dict, representation_id: str) -> None:
    """Function to update the container data from
    the related json file in .pureref_metadata/{workfile}/container
    when updating or switching asset(s)

    Args:
        container (dict): container
        representation_id (str): representation id
    """
    old_container_data = []
    data = {}
    name = container["objectName"]
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, PUREREF_SECTION_NAME_CONTAINERS).replace(
            "\\", "/"
        )
    js_fname = next((jfile for jfile in os.listdir(json_dir)
                     if jfile.endswith(f"{name}.json")), None)
    if js_fname:
        with open(f"{json_dir}/{js_fname}", "r") as file:
            old_container_data = json.load(file)
            print(f"data: {type(old_container_data)}")
            file.close()

        open(f"{json_dir}/{js_fname}", 'w').close()
        for item in old_container_data:
            item["representation"] = representation_id
            data.update(item)
        with open(f"{json_dir}/{js_fname}", "w") as file:
            new_container_data = json.dumps([data])
            file.write(new_container_data)
            file.close()


def get_instance_workfile_metadata() -> list[dict]:
    """Get instance data from the related metadata json("instances.json")
    which stores in .pureref_metadata/{workfile}/instances folder
    in the project work directory.

    Instance data includes the info like the workfile instance
    and any instances created by the users for publishing.

    Returns:
        list[dict]: instance data
    """
    file_content = []
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, PUREREF_SECTION_NAME_INSTANCES).replace(
            "\\", "/"
        )
    if not os.path.exists(json_dir) or not os.listdir(json_dir):
        return file_content
    for file in os.listdir(json_dir):
        with open(f"{json_dir}/{file}", "r") as data:
            file_content = json.load(data)

    return file_content


def remove_container_data(name: str) -> None:
    """Function to remove the specific container data from
    {subset_name}.json in .pureref_metadata/{workfile}/containers folder

    Args:
        name (str): object name stored in the container
    """
    current_file = registered_host().get_current_workfile()
    if current_file:
        current_file = os.path.splitext(
            os.path.basename(current_file))[0].strip()
    work_dir = get_workdir()
    json_dir = os.path.join(
        work_dir, ".pureref_metadata",
        current_file, PUREREF_SECTION_NAME_CONTAINERS).replace(
            "\\", "/"
        )
    all_fname_list = os.listdir(json_dir)
    json_file = next((jfile for jfile in all_fname_list
                               if jfile == f"{name}.json"), None)
    if json_file:
        os.remove(f"{json_dir}/{json_file}")


def remove_tmp_data() -> None:
    """Remove all temporary data which is created by AYON without
    saving changes when launching pureref without enabling `skip
    opening last workfile`

    """
    work_dir = get_workdir()
    for name in [PUREREF_METADATA_CREATE_CONTEXT,
                 PUREREF_SECTION_NAME_INSTANCES,
                 PUREREF_SECTION_NAME_CONTAINERS]:
        # PureRef would launch untitled.pur file from
        # temp directory when there is no last workfile.
        json_dir = os.path.join(
            work_dir, ".pureref_metadata", "untitled", name).replace(
                "\\", "/"
            )
        if not os.path.exists(json_dir):
            continue
        all_fname_list = [jfile for jfile in os.listdir(json_dir)
                          if jfile.endswith("json")]
        for fname in all_fname_list:
            os.remove(f"{json_dir}/{fname}")


def show_tools_dialog() -> None:
    """Show dialog with tools.

    Dialog will stay visible.
    """
    from ayon_pureref.api import tools_ui

    tools_ui.show_tools_dialog()
