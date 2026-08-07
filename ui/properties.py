import bpy


class PanelProperties(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_label = "Fulcrum"


class FULCRUM_PT_render(PanelProperties):
    bl_context = "render"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {"CYCLES"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("fulcrum.anim_time_limit", icon="MOD_TIME")
        col.operator("fulcrum.benchmark", icon="SORTTIME")
        col.operator("fulcrum.render_markers", icon="MARKER")


class FULCRUM_PT_data(PanelProperties):
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("fulcrum.vert_group_2_col", icon="COLOR")


registry = [
    FULCRUM_PT_render,
    FULCRUM_PT_data,
]
