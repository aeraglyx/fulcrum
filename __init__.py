bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 4, 0),
	"version": (0, 1, 14),
	"location": "Everywhere",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy
from bpy.app.handlers import persistent

from .ops.file_stuff import (
	AX_OT_save_as_new_version,
	AX_OT_go_to_latest_version,
	AX_OT_open_script_dir,
	AX_OT_open_blend_dir)
from .ops.render import (
	AX_OT_set_render_passes,
	AX_OT_anim_time_limit,
	AX_OT_render_to_new_slot)
from .ops.nodes import (
	AX_OT_node_flow,
	AX_OT_unused_nodes,
	AX_OT_find_inputs,
	AX_OT_center_nodes,
	AX_OT_nodes_to_grid,
	AX_OT_add_todo_note,
	AX_OT_hide_group_inputs,
	AX_OT_align_nodes,
	AX_OT_align_nodes_v2,
	AX_OT_tex_to_name,
	AX_OT_set_gn_defaults,
	AX_OT_reset_gn_defaults,
	AX_OT_reset_node_color)
from .ops.node_versioning import AX_OT_version_encode, AX_OT_version_decode
from .ops.three_d import (
	AX_OT_locate_vertex,
	AX_OT_locate_vertices,
	AX_OT_duplicates_to_instances,
	AX_OT_cloth_vert_mass,
	AX_OT_set_auto_smooth,
	AX_OT_hybrid_subdiv,
	AX_OT_vert_group_2_col)
from .ops.camera import (
	AX_OT_dof_setup,
	AX_OT_isometric_setup,
	AX_OT_projection_setup,
	AX_OT_frame_range_from_cam,
	AX_OT_set_resolution,
	AX_OT_set_aspect_ratio,
	AX_OT_passepartout)
from .ops.paint import AX_OT_set_paint_brush, AX_OT_set_weight_brush
from .ops.compare import AX_OT_compare, my_properties, AX_OT_benchmark
from .ops.copy_pasta import AX_OT_copy_nodes, AX_OT_paste_nodes
from .ui import (
	AX_PT_optimization,
	AX_PT_node_tools,
	AX_PT_node_group,
	AX_PT_utility_node,
	AX_PT_render,
	AX_PT_data,
	AX_PT_physics,
	AX_PT_versioning,
	AX_PT_ease_of_access,
	AX_PT_paint,
	AX_PT_utility_3d,
	AX_PT_camera,
	AX_PT_3d_stuff,
	AX_PT_3d_axis_selection)

classes = (
	my_properties,
	
	AX_OT_benchmark,
	AX_OT_anim_time_limit,
	AX_OT_vert_group_2_col,
	AX_OT_set_paint_brush,
	AX_OT_set_weight_brush,

	AX_OT_open_script_dir,
	AX_OT_open_blend_dir,
	AX_OT_save_as_new_version,
	AX_OT_go_to_latest_version,
	
	AX_OT_reset_node_color,
	AX_OT_compare,
	AX_OT_node_flow,
	AX_OT_unused_nodes,
	AX_OT_find_inputs,
	AX_OT_center_nodes,
	AX_OT_nodes_to_grid,
	AX_OT_hide_group_inputs,
	AX_OT_set_gn_defaults,
	AX_OT_reset_gn_defaults,
	AX_OT_add_todo_note,
	AX_OT_version_encode,
	AX_OT_version_decode,
	AX_OT_copy_nodes,
	AX_OT_paste_nodes,
	AX_OT_align_nodes,
	AX_OT_align_nodes_v2,
	AX_OT_tex_to_name,

	AX_OT_render_to_new_slot,
	AX_OT_set_render_passes,

	AX_OT_dof_setup,
	AX_OT_isometric_setup,
	AX_OT_projection_setup,
	AX_OT_frame_range_from_cam,
	AX_OT_passepartout,
	AX_OT_set_aspect_ratio,
	AX_OT_set_resolution,

	AX_OT_hybrid_subdiv,
	AX_OT_locate_vertex,
	AX_OT_locate_vertices,
	AX_OT_duplicates_to_instances,
	AX_OT_cloth_vert_mass,
	AX_OT_set_auto_smooth,

	AX_PT_versioning,
	AX_PT_ease_of_access,
	AX_PT_3d_stuff,
	AX_PT_3d_axis_selection,
	AX_PT_camera,
	AX_PT_paint,
	AX_PT_utility_3d,
	
	AX_PT_node_tools,
	AX_PT_node_group,
	AX_PT_optimization,
	AX_PT_utility_node,

	AX_PT_render,
	AX_PT_data,
	AX_PT_physics,
)

addon_keymaps = []

from .functions import *
import time

def unused_nodes():
	use_node_handler = bpy.context.scene['use_node_handler']
	if use_node_handler:
		start_time = time.perf_counter()
		tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
		nodes = tree.nodes
		
		clear_node_color(nodes)

		used = set()
		def func(node_current):
			used.add(node_current)
			used.add(node_current.parent)
			for input in (x for x in node_current.inputs if x.enabled):  # TODO enabled and muted for both inputs and links?
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
		print(f"handler - {time.perf_counter() - start_time}")

# def color_nodes_by_type():
# 	tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
# 	nodes = tree.nodes

# 	clear_node_color(nodes)
# 	for node in nodes:
#		# bpy.context.preferences.themes[0].node_editor.geometry_node
# 		node.use_custom_color = True
# 		node.color = color
	

@persistent
def ax_depsgraph_handler(scene):
	# print(bpy.context.area.id_data.name)
	if hasattr(bpy.context, 'selected_nodes'):
		unused_nodes()


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.ax_compare = bpy.props.PointerProperty(type=my_properties)
	bpy.types.Scene.use_node_handler = bpy.props.BoolProperty(
		name='Use Node Handler',
		default=False,
	)
	bpy.app.handlers.depsgraph_update_post.append(ax_depsgraph_handler)
	
	print("FULCRUM registered")

def unregister():

	for handler in bpy.app.handlers.render_complete:
		if handler.__name__ == 'ax_depsgraph_handler':
			bpy.app.handlers.depsgraph_update_post.remove(handler)
	del bpy.types.Scene.use_node_handler
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.ax_compare
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()