import bpy
import sys

from .functions import *
from .ops.file_stuff import is_current_file_version

# ---------------- TOPBAR ----------------


def draw_topbar(self, context):
    # red - 	STRIP_COLOR_01
    # orange - 	STRIP_COLOR_02
    # yellow - 	STRIP_COLOR_03
    # green - 	STRIP_COLOR_04
    # blue - 	STRIP_COLOR_05
    # purple - 	STRIP_COLOR_06
    # pink - 	STRIP_COLOR_07

    if context.region.alignment != "RIGHT":
        layout = self.layout
        if bpy.data.is_saved:
            if is_current_file_version():
                if bpy.data.is_dirty:
                    layout.label(text="Latest but not saved.", icon="STRIP_COLOR_07")
                else:
                    layout.label(text="DON'T PANIC!", icon="STRIP_COLOR_05")
                # layout.operator("fulcrum.go_to_latest_version", icon='STRIP_COLOR_04')
            else:
                layout.label(text="Not the latest version!", icon="STRIP_COLOR_01")
                layout.operator(
                    "fulcrum.go_to_latest_version",
                    text="Go to Latest",
                    icon="LOOP_FORWARDS",
                )
        else:
            layout.label(text="File not saved!", icon="STRIP_COLOR_01")


def draw_outliner(self, context):
    if context.space_data.display_mode == "SCENES":
        self.layout.operator(
            "fulcrum.view_layers_to_muted_nodes", text="", icon="TRIA_LEFT"
        )


def draw_timeline(self, context):
    if context.area.ui_type == "TIMELINE":
        scene = context.scene
        if scene.use_preview_range:
            frame_start = scene.frame_preview_start
            frame_end = scene.frame_preview_end
        else:
            frame_start = scene.frame_start
            frame_end = scene.frame_end
        frame_count = frame_end - frame_start + 1
        seconds = frame_count / scene.render.fps
        self.layout.label(text=f"{frame_count} | {seconds:.2f}s")


def draw_material(self, context):
    self.layout.operator(
        "fulcrum.reduce_materials", icon="TRASH"
    )  # REMOVE TRASH MATERIAL


def register_menus_and_headers():
    # bpy.types.TOPBAR_HT_upper_bar.append(draw_topbar)
    bpy.types.OUTLINER_HT_header.append(draw_outliner)
    bpy.types.DOPESHEET_HT_header.append(draw_timeline)
    bpy.types.MATERIAL_MT_context_menu.append(draw_material)


def unregister_menus_and_headers():
    # bpy.types.TOPBAR_HT_upper_bar.remove(draw_topbar)
    bpy.types.OUTLINER_HT_header.remove(draw_outliner)
    bpy.types.DOPESHEET_HT_header.remove(draw_timeline)
    bpy.types.MATERIAL_MT_context_menu.remove(draw_material)


# ---------------- PROPERTIES ----------------


class FULCRUM_PT_render(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {"CYCLES"}
    bl_label = "Fulcrum"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("fulcrum.anim_time_limit", icon="RENDER_ANIMATION")
        layout.operator("fulcrum.benchmark", icon="NONE")
        # layout.operator("fulcrum.render_to_new_slot", icon='RENDER_RESULT')


class FULCRUM_PT_data(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Fulcrum"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("fulcrum.vert_group_2_col", icon="COLOR")


# ---------------- NODE EDITOR ----------------


class NodePanel(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Fulcrum"


class FULCRUM_PT_fulcrum_node(NodePanel, bpy.types.Panel):
    bl_label = "FULCRUM"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("fulcrum.update_fulcrum", text="Update", icon="FILE_REFRESH")
        layout.label(text=f"v{get_addon_version('Fulcrum')}")


class FULCRUM_PT_node_tools(NodePanel, bpy.types.Panel):
    bl_label = "Node Tools"

    def draw(self, context):
        experimental = context.preferences.addons[__package__].preferences.experimental
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("fulcrum.reset_node_color", text="", icon="X")
        grey = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_09")
        grey.color = [0.34, 0.34, 0.34]
        red = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_01")
        red.color = [0.59, 0.18, 0.22]
        orange = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_02")
        orange.color = [0.64, 0.38, 0.21]
        yellow = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_03")
        yellow.color = [0.56, 0.51, 0.25]
        green = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_04")
        green.color = [0.26, 0.50, 0.29]
        blue = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_05")
        blue.color = [0.22, 0.40, 0.50]
        purple = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_06")
        purple.color = [0.38, 0.28, 0.51]
        pink = row.operator("fulcrum.set_node_color", text="", icon="STRIP_COLOR_07")
        pink.color = [0.52, 0.33, 0.44]

        # TODO use strip colors from theme?

        col = layout.column(align=True)
        # col.label(text="Size:", icon='FIXED_SIZE')
        row = col.row(align=True)
        default = row.operator("fulcrum.set_node_size", text="Def.")
        default.size = 1.0
        two = row.operator("fulcrum.set_node_size", text="2x")
        two.size = 2.0
        four = row.operator("fulcrum.set_node_size", text="4x")
        four.size = 4.0

        col = layout.column(align=True)
        # col.label(text="Alignment:", icon='ALIGN_CENTER')
        row = col.row(align=True)
        row.operator("fulcrum.align_nodes", text="Auto")
        row.operator("fulcrum.center_nodes", text="Center")
        row.operator("fulcrum.nodes_to_grid", text="Grid")
        if experimental:
            col.operator("fulcrum.align_nodes_v2", icon="ALIGN_CENTER")
            col.operator("fulcrum.color_node_flow", icon="COLOR")
            col.operator("fulcrum.randomize_node_color", icon="COLOR")

        col = layout.column(align=True)
        layout.operator("fulcrum.add_todo_note", icon="TEXT")  # FONT_DATA EVENT_A

        if experimental:
            col = layout.column(align=True)
            col.prop(context.scene.fulcrum, "use_node_handler")
            if context.scene.fulcrum.use_node_handler:
                col.prop(context.scene.fulcrum, "node_vis_type", text="")

        # col = layout.column(align=True)
        # row = col.row(align=True)
        # row.operator("fulcrum.copy_nodes", text="Copy", icon='COPYDOWN')
        # row.operator("fulcrum.paste_nodes", text="Pasta", icon='PASTEDOWN')

        if context.area.ui_type == "ShaderNodeTree":
            if context.space_data.shader_type == "OBJECT":
                col = layout.column(align=True)
                col.label(text="Texture Name to:", icon="TEXTURE")
                row = col.row(align=True)
                mat = row.operator("fulcrum.tex_to_name", text="Mat")  # NODE_MATERIAL
                mat.mat = True
                mat.obj = False
                obj = row.operator("fulcrum.tex_to_name", text="Obj")  # OBJECT_DATA
                obj.mat = False
                obj.obj = True
                both = row.operator("fulcrum.tex_to_name", text="Both")
                both.mat = True
                both.obj = True

        if experimental:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.operator("fulcrum.version_encode", text="Encode", icon="SYSTEM")
            row.operator("fulcrum.version_decode", text="Decode", icon="ZOOM_ALL")


class FULCRUM_PT_node_group(NodePanel, bpy.types.Panel):
    bl_label = "Group"

    @classmethod
    def poll(cls, context):
        return True  # TODO jestli jsem v groupe

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.hide_group_inputs", icon="HIDE_ON")
        col.operator("fulcrum.rename_group_input", icon="SORTALPHA")  # FONT_DATA
        col.operator(
            "fulcrum.remove_unused_group_inputs",
            text="Remove Unused Inputs",
            icon="REMOVE",
        )  # PANEL_CLOSE

        # TODO
        # col = layout.column(align=True)
        # col.label(text="Defaults:")
        # row = col.row(align=True)
        # row.operator("fulcrum.set_gn_defaults", text="(Set Defaults)")
        # row.operator("fulcrum.reset_gn_defaults", text="(Reset Defaults)")


class FULCRUM_PT_compositor(NodePanel, bpy.types.Panel):
    bl_label = "Compositor"

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "CompositorNodeTree"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("fulcrum.set_render_passes", icon="NODE_COMPOSITING")
        col.operator("fulcrum.copy_passes", icon="DUPLICATE")
        col.operator("fulcrum.remove_unused_output_sockets", icon="REMOVE")
        col = layout.column(align=True)
        col.operator("fulcrum.set_output_directory", icon="FILE_FOLDER")
        col.operator("fulcrum.compositor_increment_version", icon="LINENUMBERS_ON")
        # row = col.row(align=True)
        # row.operator("fulcrum.compositor_increment_version", text="Ver. Down", icon='TRIA_DOWN')
        # row.operator("fulcrum.compositor_increment_version", text="Ver. Up", icon='TRIA_UP')
        col = layout.column(align=True)
        col.operator("fulcrum.compositor_output_path_to_node_name", icon="FONT_DATA")
        col.operator(
            "fulcrum.view_layers_to_muted_nodes",
            text="Layers to Muted Nodes",
            icon="TRIA_LEFT",
        )
        col.operator("fulcrum.prepare_for_render", icon="RESTRICT_RENDER_OFF")


class FULCRUM_PT_find_nodes(NodePanel, bpy.types.Panel):
    bl_label = "Find"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        # col.label(text="Find:", icon='VIEWZOOM')
        row = col.row(align=True)
        row.operator("fulcrum.select_node_inputs", text="Inputs")
        row.operator("fulcrum.select_node_dependencies", text="Deps")
        row = col.row(align=True)
        row.operator("fulcrum.select_group_inputs", text="Group Inputs")
        row.operator("fulcrum.select_unused_nodes", text="Unused")


class FULCRUM_PT_optimization(NodePanel, bpy.types.Panel):
    bl_label = "Optimization"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ShaderNodeTree"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fulcrum
        row = layout.row()
        row.operator("fulcrum.compare", icon="NONE")  # SORTTIME TIME TEMP
        col = layout.column(align=True)
        col.label(
            text=f"Ratio: {props.result:.3f}", icon="SETTINGS"
        )  # UV_SYNC_SELECT CONSTRAINT SETTINGS
        col.label(
            text=f"Confidence: {props.confidence*100:.0f}%", icon="RNDCURVE"
        )  # INDIRECT_ONLY_ON RNDCURVE


class FULCRUM_PT_utility_node(NodePanel, bpy.types.Panel):
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.open_blend_file_dir", icon="FILE_BACKUP")
        col.operator("fulcrum.open_blender_user_dir", icon="SCRIPT")  # FOLDER_REDIRECT  SCRIPT

        col = layout.column(align=True)
        col.operator(
            "fulcrum.open_addon_preferences",
            text="Addon Preferences",
            icon="PREFERENCES",
        )
        if sys.platform == "win32":
            col.operator("wm.console_toggle", icon="CONSOLE")


# ---------------- VIEW 3D ----------------


class View3DPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fulcrum"


class FULCRUM_PT_fulcrum_3d(View3DPanel, bpy.types.Panel):
    bl_label = "FULCRUM"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.operator("fulcrum.update_fulcrum", text="Update", icon="FILE_REFRESH")
        layout.label(text=f"v{get_addon_version('Fulcrum')}")


class FULCRUM_PT_ease_of_access(View3DPanel, bpy.types.Panel):
    bl_label = "Ease of Access"

    def draw(self, context):
        layout = self.layout

        layout.operator("fulcrum.prepare_for_render", icon="RESTRICT_RENDER_OFF")

        # TODO scene from context
        layout.prop(bpy.data.scenes["Scene"].render, "film_transparent")
        layout.prop(bpy.data.scenes["Scene"].view_settings, "exposure")


class FULCRUM_PT_camera(View3DPanel, bpy.types.Panel):
    bl_idname = "FULCRUM_PT_camera"
    bl_label = "Camera"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.frame_range_from_cam", icon="ARROW_LEFTRIGHT")
        col.operator("fulcrum.markers_to_cameras", icon="TRIA_RIGHT")
        col.operator("fulcrum.cameras_to_markers", icon="TRIA_LEFT")

        layout.prop(context.area.spaces.active, "lock_camera")


class FULCRUM_PT_3d_stuff(View3DPanel, bpy.types.Panel):
    bl_label = "Stuff"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.edit_light_power", icon="LIGHT")
        col.operator("fulcrum.mirror", icon="MOD_MIRROR")

        col = layout.column(align=True)
        col.operator("fulcrum.obj_backup", icon="DUPLICATE")
        col.operator("fulcrum.duplicates_to_instances", icon="MOD_INSTANCE")

        if context.preferences.addons[__package__].preferences.experimental:
            col = layout.column(align=True)
            col.operator("fulcrum.locate_vertex", icon="VERTEXSEL")
            col.operator("fulcrum.locate_vertices", icon="SNAP_VERTEX")
            col.operator("fulcrum.center_render_region", icon="BORDERMOVE")


class FULCRUM_PT_camera_sub(View3DPanel, bpy.types.Panel):
    bl_parent_id = "FULCRUM_PT_camera"
    bl_label = "Extra"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.isometric_setup", icon="FILE_3D")  # VIEW_ORTHO  FILE_3D
        col.operator("fulcrum.dof_setup", icon="CAMERA_DATA")
        col.operator(
            "fulcrum.projection_setup", icon="MOD_UVPROJECT"
        )  # STICKY_UVS_LOC  UV  MOD_UVPROJECT  IMAGE_PLANE

        col = layout.column(align=True)
        col.label(text="Set Passepartout:")
        row = col.row(align=True)
        passepartout_none = row.operator("fulcrum.passepartout", text="None")
        passepartout_none.alpha = 0.0
        passepartout_normal = row.operator("fulcrum.passepartout", text="0.9")
        passepartout_normal.alpha = 0.9
        passepartout_full = row.operator("fulcrum.passepartout", text="Full")
        passepartout_full.alpha = 1.0

        col = layout.column(align=True)
        col.operator("fulcrum.set_cam_scale", icon="DRIVER_DISTANCE")


class FULCRUM_PT_3d_axis_selection(View3DPanel, bpy.types.Panel):
    # FIXME
    bl_label = "Axis Selection"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        keymap_items = (
            bpy.data.window_managers["WinMan"]
            .keyconfigs["Blender user"]
            .keymaps["3D View"]
            .keymap_items
        )

        for item in keymap_items:
            if item.idname == "transform.translate" and item.type == "G":
                transform = item
                break
        col = layout.column(align=True)
        col.label(text="Translation:")  # CON_LOCLIKE
        row = col.row(align=True)
        row.prop(
            transform.properties, "constraint_axis", text="", toggle=True, slider=True
        )

        for item in keymap_items:
            if item.idname == "transform.rotate" and item.type == "R":
                transform = item
                break
        col = layout.column(align=True)
        col.label(text="Rotation:")  # CON_ROTLIKE
        row = col.row(align=True)
        row.prop(
            transform.properties, "constraint_axis", text="", toggle=True, slider=True
        )


class FULCRUM_PT_paint(View3DPanel, bpy.types.Panel):
    bl_label = "Paint"

    @classmethod
    def poll(cls, context):
        is_weight = context.mode == "PAINT_WEIGHT"
        is_paint = context.mode == "PAINT_VERTEX"
        return is_weight or is_paint

    def draw(self, context):
        layout = self.layout
        if bpy.context.mode == "PAINT_VERTEX":
            col = layout.column(align=True)
            row = col.row(align=True)
            props = row.operator("fulcrum.set_paint_brush", text="R", icon="NONE")
            props.color = (1.0, 0.0, 0.0)
            props = row.operator("fulcrum.set_paint_brush", text="G", icon="NONE")
            props.color = (0.0, 1.0, 0.0)
            props = row.operator("fulcrum.set_paint_brush", text="B", icon="NONE")
            props.color = (0.0, 0.0, 1.0)

            row = col.row(align=True)
            props = row.operator("fulcrum.set_paint_brush", text="Blegh", icon="NONE")
            props.color = (0.0, 0.0, 0.0)
            props = row.operator("fulcrum.set_paint_brush", text="Grey", icon="NONE")
            props.color = (0.5, 0.5, 0.5)
            props = row.operator("fulcrum.set_paint_brush", text="White", icon="NONE")
            props.color = (1.0, 1.0, 1.0)

        if bpy.context.mode == "PAINT_WEIGHT":
            row = layout.row(align=True)
            props = row.operator("fulcrum.set_weight_brush", text="0.0", icon="NONE")
            props.weight = 0.0
            props = row.operator("fulcrum.set_weight_brush", text="0.5", icon="NONE")
            props.weight = 0.5
            props = row.operator("fulcrum.set_weight_brush", text="1.0", icon="NONE")
            props.weight = 1.0


class FULCRUM_PT_utility_3d(View3DPanel, bpy.types.Panel):
    bl_label = "Utility"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("fulcrum.open_blend_file_dir", icon="FILE_BACKUP")
        row.operator("fulcrum.copy_path_to_clipboard", text="", icon="COPYDOWN")
        col.operator("fulcrum.open_blender_user_dir", icon="SCRIPT")  # FOLDER_REDIRECT  SCRIPT
        col.operator("fulcrum.background_render_string", icon="SCRIPT")  # FOLDER_REDIRECT  SCRIPT

        col = layout.column(align=True)
        col.operator(
            "fulcrum.open_addon_preferences",
            text="Addon Preferences",
            icon="PREFERENCES",
        )
        if sys.platform == "win32":
            col.operator("wm.console_toggle", icon="CONSOLE")


# ---------------- CLIP_EDITOR ----------------

# class ClipEditorPanel(bpy.types.Panel):
#     bl_space_type = "CLIP_EDITOR"
#     bl_region_type = "TOOLS"  # left - TOOLS, right - UI
#     bl_category = "Fulcrum"


class FULCRUM_PT_tracker(bpy.types.Panel):
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"  # left - TOOLS, right - UI
    bl_category = "Solve"
    bl_label = "Fulcrum"

    def draw(self, context):
        layout = self.layout
        # col = layout.column(align=True)
        layout.operator("fulcrum.auto_marker_weight", icon="TRACKER")
