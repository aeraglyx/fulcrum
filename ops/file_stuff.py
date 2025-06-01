import os
import re
import subprocess

import bpy

from ..functions import *

# import string


def get_name_and_version(name):
    if not name[-1].isdigit():
        base_name = name.rstrip("_- ")  # string.punctuation
        return base_name, 0
    base_name = re.sub(r"[\s_-]*[vV]?\d+$", "", name)
    v = int(re.search(r"\d+$", name).group())
    return base_name, v


def get_newest_version():
    folder_path = bpy.path.abspath("//")
    # if not folder_path:
    # 	return True
    name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
    current_name, current_version = get_name_and_version(name)
    # newest_version = -1
    for file in os.listdir(folder_path):
        split = os.path.splitext(file)
        if split[-1].lower() == ".blend":
            new_name, new_version = get_name_and_version(split[0])
            if current_name != new_name:
                continue
            if current_version < new_version:
                current_version = new_version
    return current_version


def get_newest_file():
    blend_file = bpy.data.filepath
    print(blend_file)
    name = os.path.splitext(bpy.path.basename(blend_file))[0]
    current_name, current_version = get_name_and_version(name)
    folder_path = bpy.path.abspath("//")
    for file in os.listdir(folder_path):
        split = os.path.splitext(file)
        if split[-1].lower() == ".blend":
            new_name, new_version = get_name_and_version(split[0])
            if current_name != new_name:
                continue
            if current_version < new_version:
                blend_file = os.path.join(folder_path, file)
                print(blend_file)
    return blend_file


def is_current_file_version():
    if not bpy.data.is_saved:
        return True
    name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
    current_version = get_name_and_version(name)[1]
    newest_version = get_newest_version()
    return current_version == newest_version


class FULCRUM_OT_go_to_latest_version(bpy.types.Operator):
    bl_idname = "fulcrum.go_to_latest_version"
    bl_label = "Jump to Latest Version"
    bl_description = "Opens the latest version of this file from the same directory"

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        latest_file = get_newest_file()
        bpy.ops.wm.open_mainfile(filepath=latest_file)
        return {"FINISHED"}


class FULCRUM_OT_open_blend_dir(bpy.types.Operator):
    bl_idname = "fulcrum.open_blend_dir"
    bl_label = "Find .blend File"
    bl_description = "Opens file explorer with the current Blender file selected"

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        path = bpy.data.filepath
        subprocess.Popen('explorer /select,"' + path + '"')
        return {"FINISHED"}


class FULCRUM_OT_copy_path_to_clipboard(bpy.types.Operator):
    bl_idname = "fulcrum.copy_path_to_clipboard"
    bl_label = "Copy File Path to Clipboard"
    bl_description = "Shift click to include the filename, Ctrl click for Discord formatting"

    include_filename: bpy.props.BoolProperty(
        name="Include Filename",
        description="Use the full filepath (directory otherwise)",
        default=False,
    )
    use_discord_formatting: bpy.props.BoolProperty(
        name="Use Discord Formatting",
        description="Adds backticks around the filepath",
        default=False,
    )

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        text = bpy.data.filepath
        if not self.include_filename:
            text = os.path.dirname(text)
        if self.use_discord_formatting:
            text = f"`{text}`"
        context.window_manager.clipboard = text
        self.report({"INFO"}, "Path copied to the clipboard.")
        return {"FINISHED"}

    def invoke(self, context, event):
        self.include_filename = event.shift
        self.use_discord_formatting = event.ctrl
        return self.execute(context)


class FULCRUM_OT_background_render_string(bpy.types.Operator):
    bl_idname = "fulcrum.background_render_string"
    bl_label = "Background Render"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bpy.data.is_saved

    def execute(self, context):
        path = bpy.data.filepath
        string = "blender -b " + path + " -a"
        bpy.context.window_manager.clipboard = string
        cd = os.path.dirname(bpy.app.binary_path)
        os.system("start cmd /k ; cd " + cd + " ^& blender -b " + path + " -a")
        self.report({"INFO"}, "Copied to clipboard.")
        return {"FINISHED"}


class FULCRUM_OT_open_script_dir(bpy.types.Operator):
    bl_idname = "fulcrum.open_script_dir"
    bl_label = "Find Script Directory"
    bl_description = "Opens folder with addons and themes"

    def execute(self, context):
        path = bpy.utils.script_path_user()
        os.startfile(path)
        return {"FINISHED"}


class FULCRUM_OT_open_addon_preferences(bpy.types.Operator):
    bl_idname = "fulcrum.open_addon_preferences"
    bl_label = "Open Addon Preferences"
    bl_description = "Open Preferences and Find Fulcrum"

    def execute(self, context):
        bpy.ops.screen.userpref_show()
        bpy.context.preferences.active_section = "ADDONS"
        bpy.data.window_managers["WinMan"].addon_search = "fulcrum"
        # bpy.ops.preferences.addon_expand(module="fulcrum")
        return {"FINISHED"}
