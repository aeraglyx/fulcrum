bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 4, 0),
	"version": (0, 1, 20),
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
	AX_OT_update_fulcrum,
	AX_OT_save_as_new_version,
	AX_OT_go_to_latest_version,
	AX_OT_open_script_dir,
	AX_OT_open_blend_dir,
	AX_OT_open_addon_preferences)
from .ops.nodes import (
	AX_OT_select_node_inputs,
	AX_OT_select_node_dependencies,
	AX_OT_select_group_inputs,
	AX_OT_select_unused_nodes,
	AX_OT_center_nodes,
	AX_OT_nodes_to_grid,
	AX_OT_add_todo_note,
	AX_OT_hide_group_inputs,
	AX_OT_remove_unused_group_inputs,
	AX_OT_align_nodes,
	AX_OT_align_nodes_v2,
	AX_OT_randomize_node_color,
	AX_OT_color_node_flow,
	AX_OT_tex_to_name,
	AX_OT_set_gn_defaults,
	AX_OT_reset_gn_defaults,
	AX_OT_set_node_color,
	AX_OT_reset_node_color,
	AX_OT_set_node_size)
from .ops.render import (
	AX_OT_set_render_passes,
	AX_OT_anim_time_limit,
	AX_OT_render_to_new_slot,
	AX_OT_set_output_directory,
	AX_OT_prepare_for_render,
	AX_OT_compositor_increment_version,
	AX_OT_view_layers_to_muted_nodes)
from .ops.node_versioning import AX_OT_version_encode, AX_OT_version_decode
from .ops.three_d import (
	AX_OT_locate_vertex,
	AX_OT_locate_vertices,
	AX_OT_duplicates_to_instances,
	AX_OT_hybrid_subdiv,
	AX_OT_obj_backup,
	AX_OT_vert_group_2_col)
from .ops.camera import (
	AX_OT_dof_setup,
	AX_OT_isometric_setup,
	AX_OT_projection_setup,
	AX_OT_frame_range_from_cam,
	AX_OT_set_resolution,
	AX_OT_set_aspect_ratio,
	AX_OT_passepartout,
	AX_OT_center_render_region)

from .ops.paint import AX_OT_set_paint_brush, AX_OT_set_weight_brush
from .ops.compare import AX_OT_compare, AX_OT_benchmark
from .ops.copy_pasta import AX_OT_copy_nodes, AX_OT_paste_nodes

from .props import fulcrum_props
from .prefs import FulcrumPreferences

from .ui import (
	draw_topbar,
	draw_outliner,
	draw_timeline,

	AX_PT_fulcrum_node,
	AX_PT_node_tools,
	AX_PT_node_group,
	AX_PT_optimization,
	AX_PT_compositor,
	AX_PT_find_nodes,
	AX_PT_utility_node,

	AX_PT_fulcrum_3d,
	AX_PT_render,
	AX_PT_data,
	AX_PT_paint,
	AX_PT_utility_3d,
	AX_PT_camera,
	AX_PT_3d_stuff,
	AX_PT_3d_axis_selection,
)

classes = (
	FulcrumPreferences,
	fulcrum_props,
	
	AX_OT_benchmark,
	AX_OT_anim_time_limit,
	AX_OT_vert_group_2_col,
	AX_OT_set_paint_brush,
	AX_OT_set_weight_brush,

	AX_OT_update_fulcrum,
	AX_OT_open_script_dir,
	AX_OT_open_blend_dir,
	AX_OT_save_as_new_version,
	AX_OT_go_to_latest_version,
	AX_OT_open_addon_preferences,
	
	AX_OT_select_node_inputs,
	AX_OT_select_node_dependencies,
	AX_OT_select_group_inputs,
	AX_OT_select_unused_nodes,

	AX_OT_set_node_color,
	AX_OT_reset_node_color,
	AX_OT_compare,
	AX_OT_center_nodes,
	AX_OT_nodes_to_grid,
	AX_OT_hide_group_inputs,
	AX_OT_remove_unused_group_inputs,
	AX_OT_set_gn_defaults,
	AX_OT_reset_gn_defaults,
	AX_OT_add_todo_note,
	AX_OT_version_encode,
	AX_OT_version_decode,
	AX_OT_copy_nodes,
	AX_OT_paste_nodes,
	AX_OT_align_nodes,
	AX_OT_align_nodes_v2,
	AX_OT_randomize_node_color,
	AX_OT_color_node_flow,
	AX_OT_tex_to_name,
	AX_OT_set_node_size,

	AX_OT_render_to_new_slot,
	AX_OT_set_render_passes,
	AX_OT_set_output_directory,
	AX_OT_prepare_for_render,
	AX_OT_compositor_increment_version,
	AX_OT_view_layers_to_muted_nodes,

	AX_OT_dof_setup,
	AX_OT_isometric_setup,
	AX_OT_projection_setup,
	AX_OT_frame_range_from_cam,
	AX_OT_passepartout,
	AX_OT_center_render_region,
	AX_OT_set_aspect_ratio,
	AX_OT_set_resolution,

	AX_OT_hybrid_subdiv,
	AX_OT_locate_vertex,
	AX_OT_locate_vertices,
	AX_OT_duplicates_to_instances,
	AX_OT_obj_backup,

	# AX_PT_versioning,
	AX_PT_fulcrum_3d,
	AX_PT_3d_stuff,
	AX_PT_camera,
	AX_PT_3d_axis_selection,
	AX_PT_paint,
	AX_PT_utility_3d,
	
	AX_PT_fulcrum_node,
	AX_PT_node_tools,
	AX_PT_node_group,
	AX_PT_compositor,
	AX_PT_find_nodes,
	# AX_PT_node_group,
	AX_PT_optimization,
	AX_PT_utility_node,

	AX_PT_render,
	AX_PT_data,
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
	bpy.types.TIME_HT_editor_buttons.prepend(draw_timeline)
	# bpy.app.handlers.depsgraph_update_post.append(ax_depsgraph_handler)
	bpy.app.handlers.load_post.append(set_restart_needed_flag)
	
	print("FULCRUM registered")

def unregister():

	for handler in bpy.app.handlers.load_post:
		if handler.__name__ == 'set_restart_needed_flag':
			bpy.app.handlers.load_post.remove(handler)
		
	bpy.types.TOPBAR_HT_upper_bar.remove(draw_topbar)
	bpy.types.OUTLINER_HT_header.remove(draw_outliner)
	bpy.types.TIME_HT_editor_buttons.remove(draw_timeline)

	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.fulcrum
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()