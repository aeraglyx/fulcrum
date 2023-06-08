import os
import subprocess

import bpy


class FULCRUM_OT_open_script_dir(bpy.types.Operator):
    bl_idname = "fulcrum.open_script_dir"
    bl_label = "Open Script Directory"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        path = bpy.utils.script_path_user()
        os.startfile(path)
        return {"FINISHED"}


class FULCRUM_OT_open_blend_dir(bpy.types.Operator):
    bl_idname = "fulcrum.open_blend_dir"
    bl_label = "Open BLEND Directory"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        # path = os.path.realpath(bpy.path.abspath("//"))  # XXX points to AHK dir when not saved
        path = bpy.data.filepath
        subprocess.Popen('explorer /select,"' + path + '"')
        return {"FINISHED"}


class FULCRUM_OT_copy_path_to_clipboard(bpy.types.Operator):
    bl_idname = "fulcrum.copy_path_to_clipboard"
    bl_label = "Open BLEND Directory"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        path = bpy.data.filepath
        bpy.context.window_manager.clipboard = path
        self.report({"INFO"}, "Copied to clipboard.")
        return {"FINISHED"}


class FULCRUM_OT_apply_onyx_theme(bpy.types.Operator):
    bl_idname = "fulcrum.apply_onyx_theme"
    bl_label = "Apply Onyx Theme"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return {"FINISHED"}
        # TODO
        bpy.ops.script.execute_preset(
            filepath="C:\\Users\\Aeraglyx\\AppData\\Roaming\\Blender Foundation\\Blender\\3.4\\scripts\\presets\\interface_theme\\onyx.xml",
            menu_idname="USERPREF_MT_interface_theme_presets",
        )
        # TODO matcap, backfacing, cavity
