import bpy
import sys

from ..functions import get_addon_version


class FULCRUM_PT_meta(bpy.types.Panel):
    bl_label = f"FULCRUM {get_addon_version()}"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("fulcrum.update_fulcrum", text="Update", icon="FILE_REFRESH")


class FULCRUM_PT_utility(bpy.types.Panel):
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("fulcrum.open_blend_file_dir", icon="FILE_BLEND")
        row.operator("fulcrum.copy_path_to_clipboard", text="", icon="COPYDOWN")
        col.operator("fulcrum.backup", icon="FILE_BACKUP")

        col = layout.column(align=True)
        col.operator("fulcrum.open_blender_user_dir", icon="FILE_SCRIPT")
        col.operator("fulcrum.background_render_string", icon="SCRIPT")

        col = layout.column(align=True)
        col.operator("fulcrum.open_addon_preferences", text="Addon Preferences", icon="PREFERENCES")
        if sys.platform == "win32":
            col.operator("wm.console_toggle", icon="CONSOLE")
