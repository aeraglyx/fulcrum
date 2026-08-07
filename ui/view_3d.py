import bpy

from .common import FULCRUM_PT_meta, FULCRUM_PT_utility
from .. import __package__ as base_package


class PanelView3D(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fulcrum"


class FULCRUM_PT_fulcrum_3d(PanelView3D, FULCRUM_PT_meta):
    pass


class FULCRUM_PT_ease_of_access(PanelView3D):
    bl_label = "Ease of Access"

    def draw(self, context):
        layout = self.layout

        layout.operator("fulcrum.prepare_for_render", icon="RESTRICT_RENDER_OFF")

        layout.prop(context.scene.render, "film_transparent")
        layout.prop(context.scene.view_settings, "exposure")


class FULCRUM_PT_camera(PanelView3D):
    bl_idname = "FULCRUM_PT_camera"
    bl_label = "Camera"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.frame_range_from_cam", icon="ARROW_LEFTRIGHT")
        col.operator("fulcrum.markers_to_cameras", icon="TRIA_RIGHT")
        col.operator("fulcrum.cameras_to_markers", icon="TRIA_LEFT")

        layout.prop(context.area.spaces.active, "lock_camera")


class FULCRUM_PT_3d_stuff(PanelView3D):
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

        if context.preferences.addons[base_package].preferences.experimental:
            col = layout.column(align=True)
            col.operator("fulcrum.locate_vertex", icon="VERTEXSEL")
            col.operator("fulcrum.locate_vertices", icon="SNAP_VERTEX")
            col.operator("fulcrum.center_render_region", icon="BORDERMOVE")


class FULCRUM_PT_camera_sub(PanelView3D):
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


class FULCRUM_PT_3d_axis_selection(PanelView3D):
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
            transform.properties, # type: ignore
            "constraint_axis", text="", toggle=True, slider=True
        )

        for item in keymap_items:
            if item.idname == "transform.rotate" and item.type == "R":
                transform = item
                break
        col = layout.column(align=True)
        col.label(text="Rotation:")  # CON_ROTLIKE
        row = col.row(align=True)
        row.prop(
            transform.properties, # type: ignore
            "constraint_axis", text="", toggle=True, slider=True
        )


class FULCRUM_PT_paint(PanelView3D):
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


class FULCRUM_PT_utility_3d(PanelView3D, FULCRUM_PT_utility):
    pass


registry = [
    FULCRUM_PT_fulcrum_3d,
    FULCRUM_PT_ease_of_access,
    FULCRUM_PT_camera,
    FULCRUM_PT_camera_sub,
    FULCRUM_PT_3d_stuff,
    FULCRUM_PT_paint,
    FULCRUM_PT_utility_3d,
]
