import random

import bpy
import mathutils

from ...functions import (
    clear_node_color,
    get_output_nodes,
    oklab_2_srgb,
)


class FULCRUM_OT_hide_group_inputs(bpy.types.Operator):
    bl_idname = "fulcrum.hide_group_inputs"
    bl_label = "Hide Group Inputs"
    bl_description = ""

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        for node in nodes:
            if node.type == "GROUP_INPUT":
                for socket in node.outputs:
                    if socket.enabled and not socket.is_linked:
                        socket.hide = True
        return {"FINISHED"}


class FULCRUM_OT_remove_unused_group_inputs(bpy.types.Operator):
    bl_idname = "fulcrum.remove_unused_group_inputs"
    bl_label = "Remove Unused Group Inputs"
    bl_description = ""
    bl_options = {"UNDO"}

    # FIXME: GeometryNodeTree has no "inputs"

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        group = nodes.id_data

        used_inputs = set()
        for node in nodes:
            if node.type == "GROUP_INPUT":
                for socket in node.outputs:
                    if socket.is_linked:  # socket.enabled
                        used_inputs.add(socket)

        self.report(
            {"INFO"}, f"Removed {len(group.inputs) - len(used_inputs)} unused inputs."
        )

        for group_input in group.inputs[:]:
            if group_input not in used_inputs:
                group.inputs.remove(group_input)

        return {"FINISHED"}


class FULCRUM_OT_select_node_inputs(bpy.types.Operator):
    bl_idname = "fulcrum.select_node_inputs"
    bl_label = "Select Node Inputs"
    bl_description = "Show all nodes used by the selected nodes"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    def execute(self, context):
        nodes = bpy.context.space_data.edit_tree.nodes
        selected = context.selected_nodes

        clear_node_color(nodes)

        nodes_out = []

        def get_input_node(input):
            for link in input.links:
                node = link.from_node
                if node.type == "REROUTE":
                    get_input_node(node.inputs[0])
                elif not node.mute:
                    nodes_out.append(node)

        for node_orig in selected:
            for input in (x for x in node_orig.inputs if x.enabled):
                get_input_node(input)

        for node in nodes:
            if node in nodes_out:
                node.select = True
            else:
                node.select = False

        bpy.ops.node.view_selected()

        return {"FINISHED"}


class FULCRUM_OT_select_node_dependencies(bpy.types.Operator):
    bl_idname = "fulcrum.select_node_dependencies"
    bl_label = "Select Node Dependencies"
    bl_description = "Show all nodes used by the selected nodes"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        selected = context.selected_nodes

        clear_node_color(nodes)

        nodes_out = []

        def func(node_current):
            for input in (x for x in node_current.inputs if x.enabled):
                for link in input.links:  # TODO links plural ? link limit
                    node = link.from_node
                    if node not in nodes_out:
                        nodes_out.append(node)
                        func(node)

        for node in selected:
            func(node)

        for node in nodes:
            if node in nodes_out:
                node.select = True
            else:
                node.select = False

        bpy.ops.node.view_selected()

        return {"FINISHED"}


class FULCRUM_OT_select_group_inputs(bpy.types.Operator):
    bl_idname = "fulcrum.select_group_inputs"
    bl_label = "Select Group Inputs"
    bl_description = ""

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        for node in nodes:
            if node.type == "GROUP_INPUT":
                node.select = True
            else:
                node.select = False

        bpy.ops.node.view_selected()

        return {"FINISHED"}


class FULCRUM_OT_select_unused_nodes(bpy.types.Operator):
    bl_idname = "fulcrum.select_unused_nodes"
    bl_label = "Select Unused Nodes"
    bl_description = "Show all nodes used by the selected nodes"

    # @classmethod
    # def poll(cls, context):
    #     return bool(context.selected_nodes)

    # TODO make it work for inside of node groups

    def execute(self, context):
        tree = context.space_data.edit_tree  # context.active_node.id_data
        nodes = tree.nodes

        clear_node_color(nodes)

        used = set()

        def func(node_current):
            used.add(node_current)
            used.add(node_current.parent)
            for input in node_current.inputs:
                if not input.enabled:
                    continue
                # TODO: muted nodes and muted links
                for link in input.links:
                    func(link.from_node)

        output_nodes = get_output_nodes(context)
        for output_node in output_nodes:
            func(output_node)

        # TODO don't delete viewer (geo, shader, ...) - check if connected to used node, otherwise yeet
        # unused = [node for node in nodes if node not in used]

        for node in nodes:
            if node in used:
                node.select = False
            else:
                node.select = True

        bpy.ops.node.view_selected()

        return {"FINISHED"}


class FULCRUM_OT_randomize_node_color(bpy.types.Operator):
    bl_idname = "fulcrum.randomize_node_color"
    bl_label = "Randomize Node Color"
    bl_description = "..."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    strength: bpy.props.FloatProperty(
        name="Strength",
        description="...",
        min=0.0,
        default=0.05,
        soft_max=1.0,
    ) # type: ignore

    def execute(self, context):
        # BUG: doesn't work in compositor
        tree = context.space_data.edit_tree
        nodes = tree.nodes

        for node in nodes:
            node.use_custom_color = True
            ab = (
                mathutils.Vector((random.uniform(-1, 1), random.uniform(-1, 1)))
                * self.strength
            )
            node.color = oklab_2_srgb(0.6, ab.x, ab.y)

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "strength")


class FULCRUM_OT_add_todo_note(bpy.types.Operator):
    bl_idname = "fulcrum.add_todo_note"
    bl_label = "Add Note"
    bl_description = ""
    bl_property = "text"

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    text: bpy.props.StringProperty(
        name="Note",
        default="TODO",
    ) # type: ignore

    def execute(self, context):
        tree = context.space_data.edit_tree
        nodes = tree.nodes
        node = nodes.new(type="NodeFrame")

        node.label = self.text
        node.width = 140
        node.height = 40
        node.location = tree.view_center + mathutils.Vector((-70, 20))

        for node in nodes:
            node.select = False

        node.select = True
        nodes.active = node

        # TODO: modal to place the node?

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        # layout.use_property_split = True
        # layout.use_property_decorate = False
        col = layout.column(align=True)
        col.prop(self, "text")


class FULCRUM_OT_tex_to_name(bpy.types.Operator):
    bl_idname = "fulcrum.tex_to_name"
    bl_label = "Tex > Mat Name"
    bl_description = (
        "Name material or object after image used by the active Image Texture node"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if context.area.ui_type == "ShaderNodeTree":
            if context.space_data.shader_type == "OBJECT":
                if hasattr(context, "active_node"):
                    node = context.active_node
                    if node and node.select and node.type == "TEX_IMAGE":
                        return bool(node.image)
        return False

    mat: bpy.props.BoolProperty(
        name="Material", description="xxx", default=True
    ) # type: ignore
    obj: bpy.props.BoolProperty(
        name="Object", description="xxx", default=True
    ) # type: ignore

    def execute(self, context):
        node = context.active_node
        img_name = ".".join(node.image.name.split(".")[:-1])
        if self.mat:
            context.material.name = img_name
        if self.obj:
            context.object.name = img_name
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "mat")
        layout.prop(self, "obj")


class FULCRUM_OT_set_node_color(bpy.types.Operator):

    """Set custom node color"""

    bl_idname = "fulcrum.set_node_color"
    bl_label = "Set Node Color"
    bl_description = "Set custom node color"

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    color: bpy.props.FloatVectorProperty(
        name="Color", subtype="COLOR", default=[0.0, 0.0, 0.0]
    ) # type: ignore

    def execute(self, context):
        nodes = context.selected_nodes  # context.active_node.id_data.nodes
        for node in nodes:
            node.use_custom_color = True
            node.color = self.color

        return {"FINISHED"}


class FULCRUM_OT_reset_node_color(bpy.types.Operator):

    """Reset custom node color"""

    bl_idname = "fulcrum.reset_node_color"
    bl_label = "Reset Node Color"
    bl_description = "Reset custom node color"

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        # nodes = context.space_data.edit_tree.nodes  # context.active_node.id_data.nodes
        for node in context.selected_nodes:
            # if node.bl_idname != 'NodeFrame':
            node.use_custom_color = False

        return {"FINISHED"}


class FULCRUM_OT_set_node_size(bpy.types.Operator):
    bl_idname = "fulcrum.set_node_size"
    bl_label = "Set Node Size"
    bl_description = ""
    bl_options = {"UNDO"}

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    size: bpy.props.FloatProperty(name="Size", default=1.0) # type: ignore

    def execute(self, context):
        nodes = context.selected_nodes
        for node in nodes:
            node.width = node.bl_width_default * self.size

        return {"FINISHED"}


class FULCRUM_OT_set_gn_defaults(bpy.types.Operator):
    bl_idname = "fulcrum.set_gn_defaults"
    bl_label = "Set GN Defaults"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        # group = context.space_data.edit_tree
        modif = context.object.modifiers.active
        group = modif.node_group

        for input in group.inputs[1:]:
            if input.default_value:
                input.default_value = modif[input.identifier]

        return {"FINISHED"}


class FULCRUM_OT_reset_gn_defaults(bpy.types.Operator):
    bl_idname = "fulcrum.reset_gn_defaults"
    bl_label = "Reset GN Defaults"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return context.area.type == "NODE_EDITOR"

    def execute(self, context):
        # group = context.space_data.edit_tree
        modif = context.object.modifiers.active
        group = modif.node_group

        for input in group.inputs[1:]:
            if input.default_value:
                modif[input.identifier] = input.default_value

        modif.show_viewport = False
        modif.show_viewport = True

        return {"FINISHED"}
