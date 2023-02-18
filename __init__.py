bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 4, 0),
	"version": (0, 1, 22),
	"location": "Everywhere. Mostly in node editor and 3D viewport.",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy
from bpy.app.handlers import persistent
from .functions import *
import time

from .ops.file_stuff import (
	FULCRUM_OT_update_fulcrum,
	FULCRUM_OT_save_as_new_version,
	FULCRUM_OT_go_to_latest_version,
	FULCRUM_OT_open_script_dir,
	FULCRUM_OT_open_blend_dir,
	FULCRUM_OT_open_addon_preferences)
from .ops.nodes import (
	FULCRUM_OT_select_node_inputs,
	FULCRUM_OT_select_node_dependencies,
	FULCRUM_OT_select_group_inputs,
	FULCRUM_OT_select_unused_nodes,
	FULCRUM_OT_center_nodes,
	FULCRUM_OT_nodes_to_grid,
	FULCRUM_OT_add_todo_note,
	FULCRUM_OT_hide_group_inputs,
	FULCRUM_OT_remove_unused_group_inputs,
	FULCRUM_OT_align_nodes,
	FULCRUM_OT_align_nodes_v2,
	FULCRUM_OT_randomize_node_color,
	FULCRUM_OT_color_node_flow,
	FULCRUM_OT_tex_to_name,
	FULCRUM_OT_set_gn_defaults,
	FULCRUM_OT_reset_gn_defaults,
	FULCRUM_OT_set_node_color,
	FULCRUM_OT_reset_node_color,
	FULCRUM_OT_set_node_size)
from .ops.render import (
	FULCRUM_OT_set_render_passes,
	FULCRUM_OT_anim_time_limit,
	FULCRUM_OT_render_to_new_slot,
	FULCRUM_OT_set_output_directory,
	FULCRUM_OT_prepare_for_render,
	FULCRUM_OT_compositor_increment_version,
	FULCRUM_OT_view_layers_to_muted_nodes)
from .ops.node_versioning import FULCRUM_OT_version_encode, FULCRUM_OT_version_decode
from .ops.three_d import (
	FULCRUM_OT_locate_vertex,
	FULCRUM_OT_locate_vertices,
	FULCRUM_OT_duplicates_to_instances,
	FULCRUM_OT_hybrid_subdiv,
	FULCRUM_OT_obj_backup,
	FULCRUM_OT_vert_group_2_col)
from .ops.camera import (
	FULCRUM_OT_dof_setup,
	FULCRUM_OT_isometric_setup,
	FULCRUM_OT_projection_setup,
	FULCRUM_OT_frame_range_from_cam,
	FULCRUM_OT_set_resolution,
	FULCRUM_OT_set_aspect_ratio,
	FULCRUM_OT_passepartout,
	FULCRUM_OT_center_render_region)

from .ops.paint import FULCRUM_OT_set_paint_brush, FULCRUM_OT_set_weight_brush
from .ops.compare import FULCRUM_OT_compare, FULCRUM_OT_benchmark
from .ops.copy_pasta import FULCRUM_OT_copy_nodes, FULCRUM_OT_paste_nodes

from .props import fulcrum_props
from .prefs import FulcrumPreferences

from .ui import (
	draw_topbar,
	draw_outliner,
	draw_timeline,

	FULCRUM_PT_fulcrum_node,
	FULCRUM_PT_node_tools,
	FULCRUM_PT_node_group,
	FULCRUM_PT_optimization,
	FULCRUM_PT_compositor,
	FULCRUM_PT_find_nodes,
	FULCRUM_PT_utility_node,

	FULCRUM_PT_fulcrum_3d,
	FULCRUM_PT_render,
	FULCRUM_PT_data,
	FULCRUM_PT_paint,
	FULCRUM_PT_utility_3d,
	FULCRUM_PT_camera,
	FULCRUM_PT_3d_stuff,
	FULCRUM_PT_3d_axis_selection,
)

classes = (
	FulcrumPreferences,
	fulcrum_props,
	
	FULCRUM_OT_benchmark,
	FULCRUM_OT_anim_time_limit,
	FULCRUM_OT_vert_group_2_col,
	FULCRUM_OT_set_paint_brush,
	FULCRUM_OT_set_weight_brush,

	FULCRUM_OT_update_fulcrum,
	FULCRUM_OT_open_script_dir,
	FULCRUM_OT_open_blend_dir,
	FULCRUM_OT_save_as_new_version,
	FULCRUM_OT_go_to_latest_version,
	FULCRUM_OT_open_addon_preferences,
	
	FULCRUM_OT_select_node_inputs,
	FULCRUM_OT_select_node_dependencies,
	FULCRUM_OT_select_group_inputs,
	FULCRUM_OT_select_unused_nodes,

	FULCRUM_OT_set_node_color,
	FULCRUM_OT_reset_node_color,
	FULCRUM_OT_compare,
	FULCRUM_OT_center_nodes,
	FULCRUM_OT_nodes_to_grid,
	FULCRUM_OT_hide_group_inputs,
	FULCRUM_OT_remove_unused_group_inputs,
	FULCRUM_OT_set_gn_defaults,
	FULCRUM_OT_reset_gn_defaults,
	FULCRUM_OT_add_todo_note,
	FULCRUM_OT_version_encode,
	FULCRUM_OT_version_decode,
	FULCRUM_OT_copy_nodes,
	FULCRUM_OT_paste_nodes,
	FULCRUM_OT_align_nodes,
	FULCRUM_OT_align_nodes_v2,
	FULCRUM_OT_randomize_node_color,
	FULCRUM_OT_color_node_flow,
	FULCRUM_OT_tex_to_name,
	FULCRUM_OT_set_node_size,

	FULCRUM_OT_render_to_new_slot,
	FULCRUM_OT_set_render_passes,
	FULCRUM_OT_set_output_directory,
	FULCRUM_OT_prepare_for_render,
	FULCRUM_OT_compositor_increment_version,
	FULCRUM_OT_view_layers_to_muted_nodes,

	FULCRUM_OT_dof_setup,
	FULCRUM_OT_isometric_setup,
	FULCRUM_OT_projection_setup,
	FULCRUM_OT_frame_range_from_cam,
	FULCRUM_OT_passepartout,
	FULCRUM_OT_center_render_region,
	FULCRUM_OT_set_aspect_ratio,
	FULCRUM_OT_set_resolution,

	FULCRUM_OT_hybrid_subdiv,
	FULCRUM_OT_locate_vertex,
	FULCRUM_OT_locate_vertices,
	FULCRUM_OT_duplicates_to_instances,
	FULCRUM_OT_obj_backup,

	# FULCRUM_PT_versioning,
	FULCRUM_PT_fulcrum_3d,
	FULCRUM_PT_3d_stuff,
	FULCRUM_PT_camera,
	FULCRUM_PT_3d_axis_selection,
	FULCRUM_PT_paint,
	FULCRUM_PT_utility_3d,
	
	FULCRUM_PT_fulcrum_node,
	FULCRUM_PT_node_tools,
	FULCRUM_PT_node_group,
	FULCRUM_PT_compositor,
	FULCRUM_PT_find_nodes,
	# FULCRUM_PT_node_group,
	FULCRUM_PT_optimization,
	FULCRUM_PT_utility_node,

	FULCRUM_PT_render,
	FULCRUM_PT_data,
)

addon_keymaps = []

def unused_nodes():
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

def node_color_levels():
	tree = bpy.context.space_data.edit_tree  # context.active_node.id_data
	nodes = tree.nodes

	used = set()
	levels = {node:0 for node in nodes}
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
#		# bpy.context.preferences.themes[0].node_editor.geometry_node
# 		node.use_custom_color = True
# 		node.color = color


	

@persistent
def ax_depsgraph_handler(scene):
	# print(bpy.context.area.id_data.name)
	use_node_handler = bpy.context.scene.fulcrum['use_node_handler']  # FIXME for the 1st time, use_node_handler isn't there
	if use_node_handler:
		start_time = time.perf_counter()
		if hasattr(bpy.context, 'selected_nodes'):
			match bpy.context.scene.fulcrum.node_vis_type:
				case 'UNUSED':
					unused_nodes()
				case 'LEVELS':
					node_color_levels()
		print(f"handler - {time.perf_counter() - start_time}")

@persistent
def set_restart_needed_flag(scene):
	use_node_handler = bpy.context.scene.fulcrum.restart_needed = False
		


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.fulcrum = bpy.props.PointerProperty(type=fulcrum_props)
	
	bpy.types.TOPBAR_HT_upper_bar.append(draw_topbar)
	bpy.types.OUTLINER_HT_header.append(draw_outliner)
	bpy.types.DOPESHEET_HT_header.append(draw_timeline)
	# bpy.app.handlers.depsgraph_update_post.append(ax_depsgraph_handler)
	bpy.app.handlers.load_post.append(set_restart_needed_flag)
	
	print("FULCRUM registered")

def unregister():

	for handler in bpy.app.handlers.load_post:
		if handler.__name__ == 'set_restart_needed_flag':
			bpy.app.handlers.load_post.remove(handler)
		
	bpy.types.TOPBAR_HT_upper_bar.remove(draw_topbar)
	bpy.types.OUTLINER_HT_header.remove(draw_outliner)
	bpy.types.DOPESHEET_HT_header.remove(draw_timeline)

	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.fulcrum
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()