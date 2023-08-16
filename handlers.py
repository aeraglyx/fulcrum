import time

import bpy
from bpy.app.handlers import persistent

from .functions import *


def unused_nodes():
    tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
    nodes = tree.nodes

    clear_node_color(nodes)

    used = set()

    def func(node_current):
        used.add(node_current)
        used.add(node_current.parent)
        for input in (
            x for x in node_current.inputs if x.enabled
        ):  # TODO enabled and muted for both inputs and links?
            for link in (x for x in input.links if not x.is_muted):
                if link.from_node not in used:
                    func(link.from_node)

    output_nodes = get_output_nodes(bpy.context)
    for output_node in output_nodes:
        func(output_node)

    # TODO don't delete viewer (geo, shader, ...) - check if connected to used node, otherwise yeet
    unused = [node for node in nodes if node not in used]

    # color_nodes(unused, [0.65, 0.29, 0.32])  # shows up darker **2.2 **0.45
    color_nodes(unused, oklab_hsl_2_srgb(0.0, 0.05, 0.6))


def node_color_levels():
    tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
    nodes = tree.nodes

    used = set()
    levels = {node: 0 for node in nodes}

    def figure_out_levels(node_current, level_current):
        used.add(node_current)
        inputs = (x for x in node_current.inputs if x.enabled)
        for input in inputs:
            for link in (x for x in input.links if not x.is_muted):
                node = link.from_node
                if levels[node] <= level_current:
                    levels[node] = level_current + 1
                    figure_out_levels(node, level_current + 1)

    root_nodes = get_output_nodes(bpy.context)
    for root_node in root_nodes:
        figure_out_levels(root_node, 0)

    clear_node_color(used)

    for node in used:
        node.use_custom_color = True
        node.color = oklab_hsl_2_srgb(-0.075 * levels[node], 0.05, 0.6)


# def color_nodes_by_type():
# 	tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
# 	nodes = tree.nodes

# 	clear_node_color(nodes)
# 	for node in nodes:
# 		# bpy.context.preferences.themes[0].node_editor.geometry_node
# 		node.use_custom_color = True
# 		node.color = color


@persistent
def ax_depsgraph_handler(scene):
    # print(bpy.context.area.id_data.name)
    use_node_handler = bpy.context.scene.fulcrum[
        "use_node_handler"
    ]  # FIXME for the 1st time, use_node_handler isn't there
    if use_node_handler:
        start_time = time.perf_counter()
        if hasattr(bpy.context, "selected_nodes"):
            match bpy.context.scene.fulcrum.node_vis_type:
                case "UNUSED":
                    unused_nodes()
                case "LEVELS":
                    node_color_levels()
        print(f"handler - {time.perf_counter() - start_time}")


# @persistent
# def set_restart_needed_flag(scene):
#     use_node_handler = bpy.context.scene.fulcrum.restart_needed = False


def register_handlers():
    pass


#     bpy.app.handlers.load_post.append(set_restart_needed_flag)
#     # bpy.app.handlers.depsgraph_update_post.append(ax_depsgraph_handler)


def unregister_handlers():
    pass


#     for handler in bpy.app.handlers.load_post:
#         if handler.__name__ == "set_restart_needed_flag":
#             bpy.app.handlers.load_post.remove(handler)
