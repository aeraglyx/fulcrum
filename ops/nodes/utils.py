import re

import bpy
import mathutils


def color_nodes(nodes, color):
    for node in nodes:
        node.use_custom_color = True
        node.color = color


def clear_node_color(nodes):
    for node in nodes:
        node.use_custom_color = False


def get_node_name(node):
    """Get node name that is visible to user"""
    if node.label:
        return node.label
    elif hasattr(node, "node_tree"):
        return node.node_tree.name
    else:
        name = node.name
        return re.sub(".[0-9]{3,}$", "", name)


def node_width(node):
    if node.type == "REROUTE":
        return 0
    return node.width


def node_height(node):
    if node.type == "REROUTE":
        return 0
    if node.hide == True:
        return 32
    return node.dimensions[1] * node.width / node.dimensions[0]


def node_size(node):
    if node.type == "REROUTE":
        return mathutils.Vector((0, 0))
    x = node.width
    y = node.dimensions[1] * node.width / node.dimensions[0]
    return mathutils.Vector((x, y))


def node_center(node):
    return node.location + node_size(node) * mathutils.Vector((0.5, -0.5))


def node_intersection(node_1, node_2):
    x = 20
    y = 20
    lx = max(node_1.location.x - x, node_2.location.x - x)
    rx = min(
        node_1.location.x + node_width(node_1) + x,
        node_2.location.x + node_width(node_2) + x,
    )
    if lx > rx:
        return None
    uy = min(node_1.location.y + y, node_2.location.y + y)
    dy = max(
        node_1.location.y - node_height(node_1) - y,
        node_2.location.y - node_height(node_2) - y,
    )
    if uy < dy:
        return None
    return (mathutils.Vector((lx, dy)), mathutils.Vector((rx - lx, uy - dy)))


def socket_loc(socket):
    X_OFFSET = -1.0
    Y_TOP = -34.0
    Y_BOTTOM = 16.0
    Y_OFFSET = 22.0

    # 2 offsets
    VEC_BOTTOM = 28.0
    VEC_TOP = 32.0

    def is_tall(socket):
        if socket.type != "VECTOR":
            return False
        if socket.hide_value:
            return False
        if socket.is_linked:
            return False
        return True

    socket_loc = mathutils.Vector((0, 0))
    node = socket.node
    if socket.is_output:
        x = node.location.x + node_width(node) + X_OFFSET
        y = node.location.y + Y_TOP
        for output in node.outputs:
            if output.hide or not output.enabled:
                continue
            if output == socket:
                socket_loc = mathutils.Vector((x, y))
            y -= Y_OFFSET
    else:
        x = node.location.x
        y = node.location.y - node_height(node) + Y_BOTTOM
        for input in reversed(node.inputs):
            if input.hide or not input.enabled:
                continue
            tall = is_tall(input)
            y += VEC_BOTTOM * tall
            if input == socket:
                socket_loc = mathutils.Vector((x, y))
            y += Y_OFFSET + VEC_TOP * tall

    return socket_loc


def get_original_tree(tree, context):
    # TODO: this relies on the fact that tree is in the current scene
    original_tree = None
    if tree.type == "GEOMETRY":
        original_tree = context.object.modifiers.active.node_group
    if tree.type == "SHADER":
        if context.space_data.shader_type == "OBJECT":
            original_tree = context.material.node_tree
        if context.space_data.shader_type == "WORLD":
            original_tree = context.scene.world.node_tree
        if context.space_data.shader_type == "LINESTYLE":
            pass  # TODO
    if tree.type == "COMPOSITING":
        original_tree = context.scene.compositing_node_group
    # if tree.type == 'TEXTURE':
    # 	original_tree = context.
    return original_tree


def is_original_tree(tree, context):
    return get_original_tree(tree, context) == tree


def is_node_group(tree):
    # return get_original_tree(tree, context) != tree
    return tree in bpy.data.node_groups


def get_output_nodes(node_tree):
    nodes = node_tree.nodes
    output_nodes = set()
    original_tree = is_original_tree(node_tree, bpy.context)

    idnames_geometry = ["NodeGroupOutput"]
    idnames_shader = [
        "ShaderNodeOutputMaterial",
        "ShaderNodeOutputWorld",
        "ShaderNodeTree",
    ]
    idnames_compositing = [
        "CompositorNodeComposite",  # main output
        "CompositorNodeViewer",
        "CompositorNodeOutputFile",
        "CompositorNodeTree",  # the what?
        "NodeGroupOutput",
    ]
    idnames_texture = ["TextureNodeTree"]
    idnames_group = ["NodeGroupOutput"]

    for node in nodes:
        if original_tree:
            match node_tree.type:
                case "GEOMETRY":
                    if node.bl_idname in idnames_geometry:
                        output_nodes.add(node)
                case "SHADER":
                    if node.bl_idname in idnames_shader and node.is_active_output:
                        output_nodes.add(node)
                case "COMPOSITING":  # 'COMPOSITE'
                    # well yes but actually no  # 'CompositorNodeTree'
                    if node.bl_idname in idnames_compositing:
                        output_nodes.add(node)
                case "TEXTURE":
                    # TODO texture doesn't work
                    if node.bl_idname in idnames_texture:
                        output_nodes.add(node)
        else:
            if node.bl_idname in idnames_group:
                output_nodes.add(node)

    return output_nodes
