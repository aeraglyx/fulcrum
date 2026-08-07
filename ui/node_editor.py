import bpy

from .common import FULCRUM_PT_meta, FULCRUM_PT_utility
from .. import __package__ as base_package


class PanelNodeEditor(bpy.types.Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Fulcrum"


class FULCRUM_PT_fulcrum_node(PanelNodeEditor, FULCRUM_PT_meta):
    pass


class FULCRUM_PT_node_tools(PanelNodeEditor):
    bl_label = "Node Tools"

    def draw(self, context):
        experimental = context.preferences.addons[base_package].preferences.experimental
        layout = self.layout

        col = layout.column(align=True)
        row = col.row(align=True)
        color_reset = row.operator("fulcrum.set_node_color", text=" ", icon="X")
        color_reset.reset = True
        color_dict = {
            1: [0.59, 0.18, 0.22],  # red
            2: [0.64, 0.38, 0.21],  # orange
            3: [0.56, 0.51, 0.25],  # yellow
            4: [0.26, 0.50, 0.29],  # green
            5: [0.22, 0.40, 0.50],  # blue
            6: [0.38, 0.28, 0.51],  # purple
            7: [0.52, 0.33, 0.44],  # pink
            9: [0.34, 0.34, 0.34],  # grey
        }
        for i in [9, 1, 2, 3, 4, 5, 6, 7]:
            color_entry = row.operator("fulcrum.set_node_color", text=" ", icon=f"STRIP_COLOR_0{i}")
            color_entry.color = color_dict[i]
            # TODO: use strip colors from theme?

        col = layout.column(align=True)
        row = col.row(align=True)
        for i in [1, 2, 4]:
            size_entry = row.operator("fulcrum.set_node_size", text=f"{i}x")
            size_entry.size = i

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("fulcrum.align_nodes", text="Auto")
        row.operator("fulcrum.center_nodes", text="Center")
        row.operator("fulcrum.nodes_to_grid", text="Grid")
        if experimental:
            col.operator("fulcrum.align_nodes_v2", icon="ALIGN_CENTER")
            col.operator("fulcrum.randomize_node_color", icon="COLOR")

        layout.operator("fulcrum.add_todo_note", icon="TEXT")  # FONT_DATA EVENT_A
        layout.operator("fulcrum.node_timestamp", icon="TAG")

        if context.area.ui_type == "ShaderNodeTree":
            if context.space_data.shader_type == "OBJECT":
                col = layout.column(align=True)
                col.label(text="Texture Name to:", icon="TEXTURE")
                row = col.row(align=True)
                def tex_to_name(label: str, mat: bool, obj: bool):
                    op = row.operator("fulcrum.tex_to_name", text=label)
                    op.mat = mat
                    op.obj = obj
                tex_to_name("Mat", mat=True, obj=False)
                tex_to_name("Obj", mat=False, obj=True)
                tex_to_name("Both", mat=True, obj=True)
                # TODO: data as well?


class FULCRUM_PT_node_group(PanelNodeEditor):
    bl_label = "Group"

    @classmethod
    def poll(cls, context):
        return True  # TODO: check if inside a group

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("fulcrum.hide_group_inputs", icon="HIDE_ON")
        col.operator(
            "fulcrum.remove_unused_group_inputs",
            text="Remove Unused Inputs",
            icon="REMOVE",
        )  # PANEL_CLOSE


class FULCRUM_PT_compositor(PanelNodeEditor):
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
        col = layout.column(align=True)
        col.operator("fulcrum.compositor_output_path_to_node_name", icon="FONT_DATA")
        col.operator(
            "fulcrum.view_layers_to_muted_nodes",
            text="Layers to Muted Nodes",
            icon="TRIA_LEFT",
        )
        col.operator("fulcrum.prepare_for_render", icon="RESTRICT_RENDER_OFF")


class FULCRUM_PT_find_nodes(PanelNodeEditor):
    bl_label = "Find"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("fulcrum.select_node_inputs", text="Inputs")
        row.operator("fulcrum.select_node_dependencies", text="Deps")
        row = col.row(align=True)
        row.operator("fulcrum.select_group_inputs", text="Group Inputs")
        row.operator("fulcrum.select_unused_nodes", text="Unused")


class FULCRUM_PT_optimization(PanelNodeEditor):
    bl_label = "Optimization"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ShaderNodeTree"

    def draw(self, context):
        layout = self.layout
        props = context.scene.fulcrum
        row = layout.row()
        # SORTTIME TIME TEMP
        row.operator("fulcrum.compare", icon="NONE")
        col = layout.column(align=True)
        col.label(text=f"Ratio: {props.result:.3f}", icon="SETTINGS")
        col.label(text=f"Confidence: {props.confidence*100:.0f}%", icon="RNDCURVE")


class FULCRUM_PT_utility_node(PanelNodeEditor, FULCRUM_PT_utility):
    pass


registry = [
    FULCRUM_PT_fulcrum_node,
    FULCRUM_PT_node_tools,
    FULCRUM_PT_node_group,
    FULCRUM_PT_compositor,
    FULCRUM_PT_find_nodes,
    FULCRUM_PT_optimization,
    FULCRUM_PT_utility_node,
]
