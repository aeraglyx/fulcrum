import bpy

import os
import io
import shutil
import zipfile
import requests

from ..functions import get_addon_version


class FULCRUM_OT_update_fulcrum(bpy.types.Operator):
    bl_idname = "fulcrum.update_fulcrum"
    bl_label = "Update Fulcrum"
    bl_description = "Update this addon. Requires a Blender restart"

    @classmethod
    def poll(cls, context):
        online_access = bpy.app.online_access
        return online_access

    def execute(self, context):
        archive_link = "https://github.com/aeraglyx/fulcrum/archive/refs/heads/master.zip"
        extensions_path = bpy.utils.user_resource('EXTENSIONS')
        fulcrum_path = os.path.join(extensions_path, "fulcrum")
        nested_path = os.path.join(fulcrum_path, "fulcrum-master")

        old_version = get_addon_version()

        shutil.rmtree(fulcrum_path, ignore_errors=True)

        r = requests.get(archive_link)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(fulcrum_path)

        for filename in os.listdir(nested_path):
            src = os.path.join(nested_path, filename)
            dst = os.path.join(fulcrum_path, filename)
            shutil.move(src, dst)

        os.rmdir(nested_path)

        new_version = get_addon_version()

        self.report(
            {"INFO"},
            f"Updated from {old_version} to {new_version}. Blender restart required.",
        )

        return {"FINISHED"}
