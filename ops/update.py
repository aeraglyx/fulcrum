import bpy

import os
import io
import shutil
import zipfile
import requests

from ..functions import get_addon_version


# TODO: wtf, fix this
class FULCRUM_OT_update_fulcrum(bpy.types.Operator):
    bl_idname = "fulcrum.update_fulcrum"
    bl_label = "Update Fulcrum"
    bl_description = "Update this addon. Blender will need to be reloaded"

    @classmethod
    def poll(cls, context):
        online_access = bpy.app.online_access
        return online_access

    def execute(self, context):
        repo_download_link = (
            "https://github.com/aeraglyx/fulcrum/archive/refs/heads/master.zip"
        )
        fulcrum_path = os.path.join(bpy.utils.script_path_user(), "addons", "fulcrum")
        nested_path = os.path.join(fulcrum_path, "fulcrum-master")

        old_version = get_addon_version("Fulcrum")

        shutil.rmtree(fulcrum_path, ignore_errors=True)

        # with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        # 	zip_ref.extractall(fulcrum_path)
        r = requests.get(repo_download_link)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(fulcrum_path)

        for filename in os.listdir(nested_path):
            src = os.path.join(nested_path, filename)
            dst = os.path.join(fulcrum_path, filename)
            shutil.move(src, dst)

        os.rmdir(nested_path)

        new_version = get_addon_version("Fulcrum")

        # context.scene.fulcrum.restart_needed = True
        self.report(
            {"INFO"},
            f"Updated from {old_version} to {new_version}. Blender reload needed.",
        )
        # bpy.ops.script.reload()

        return {"FINISHED"}
