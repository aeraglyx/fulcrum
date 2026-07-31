import bpy

import os
import io
import shutil
import zipfile
import requests

from ..functions import get_addon_version, get_addon_dir


def update_ext_from_gh(extension_path, repo, branch="main"):
    archive_link = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    extension_name = repo.split("/")[-1]

    os.makedirs(extension_path, exist_ok=True)
    shutil.rmtree(extension_path, ignore_errors=True)

    r = requests.get(archive_link)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(extension_path)

    nested_path = os.path.join(extension_path, f"{extension_name}-{branch}")
    for filename in os.listdir(nested_path):
        src = os.path.join(nested_path, filename)
        dst = os.path.join(extension_path, filename)
        shutil.move(src, dst)

    os.rmdir(nested_path)


class FULCRUM_OT_update_fulcrum(bpy.types.Operator):
    bl_idname = "fulcrum.update_fulcrum"
    bl_label = "Update Fulcrum"
    bl_description = "Update this addon. Requires a Blender restart"

    @classmethod
    def poll(cls, context):
        if not bpy.app.online_access:
            cls.poll_message_set("Requires online access")
            return False
        return True

    def execute(self, context):
        extension_path = get_addon_dir()
        if os.path.islink(extension_path):
            self.report({"WARNING"}, f"Addon is symlinked.")
            return {"CANCELLED"}

        version_old = get_addon_version()
        update_ext_from_gh(extension_path, repo="aeraglyx/fulcrum", branch="master")
        version_new = get_addon_version()

        self.report(
            {"INFO"},
            f"Updated from {version_old} to {version_new}. Blender restart required.",
        )

        return {"FINISHED"}


registry = [FULCRUM_OT_update_fulcrum]
