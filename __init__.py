bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 1, 0),
	"version": (0, 1, 9),
	"location": "Everywhere",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy
from bpy.app.handlers import persistent

from .operators.compare import AX_OT_compare, my_properties, AX_OT_benchmark
from .operators.reset_node_color import AX_OT_reset_node_color
from .operators.render_in_time import AX_OT_anim_time_limit
from .operators.vert_group_2_col import AX_OT_vert_group_2_col
from .operators.paint import AX_OT_set_paint_brush, AX_OT_set_weight_brush
from .operators.node_flow import AX_OT_node_flow, AX_OT_unused_nodes, AX_OT_find_inputs, AX_OT_center_nodes, AX_OT_nodes_to_grid, AX_OT_add_todo_note
from .operators.versioning import AX_OT_version_encode, AX_OT_version_decode
from .operators.utility import AX_OT_open_script_dir, AX_OT_open_blend_dir
from .operators.copy_pasta import AX_OT_copy_nodes, AX_OT_paste_nodes
from .operators.render_slots import AX_OT_render_to_new_slot
from .operators.three_d import AX_OT_locate_vertex, AX_OT_locate_vertices, AX_OT_cloth_vert_mass, AX_OT_set_auto_smooth, AX_OT_hybrid_subdiv
from .operators.camera import AX_OT_dof_setup, AX_OT_isometric_setup, AX_OT_projection_setup, AX_OT_frame_range_from_cam, AX_OT_passepartout
from .operators.render import AX_OT_set_render_passes

from . ui import (
	AX_PT_optimization,
	AX_PT_node_tools,
	AX_PT_utility_node,
	AX_PT_render,
	AX_PT_data,
	AX_PT_physics,
	AX_PT_ease_of_access,
	AX_PT_paint,
	AX_PT_utility_3d,
	AX_PT_camera_stuff,
	AX_PT_3d_stuff
)

classes = (
	my_properties,
	
	AX_OT_benchmark,
	AX_OT_anim_time_limit,
	AX_OT_vert_group_2_col,
	AX_OT_set_paint_brush,
	AX_OT_set_weight_brush,

	AX_OT_open_script_dir,
	AX_OT_open_blend_dir,
	
	AX_OT_reset_node_color,
	AX_OT_compare,
	AX_OT_node_flow,
	AX_OT_unused_nodes,
	AX_OT_find_inputs,
	AX_OT_center_nodes,
	AX_OT_nodes_to_grid,
	AX_OT_add_todo_note,
	AX_OT_version_encode,
	AX_OT_version_decode,
	AX_OT_copy_nodes,
	AX_OT_paste_nodes,

	AX_OT_render_to_new_slot,
	AX_OT_set_render_passes,

	AX_OT_dof_setup,
	AX_OT_isometric_setup,
	AX_OT_projection_setup,
	AX_OT_frame_range_from_cam,
	AX_OT_passepartout,

	AX_OT_hybrid_subdiv,
	AX_OT_locate_vertex,
	AX_OT_locate_vertices,
	AX_OT_cloth_vert_mass,
	AX_OT_set_auto_smooth,

	AX_PT_ease_of_access,
	AX_PT_3d_stuff,
	AX_PT_camera_stuff,
	AX_PT_paint,
	AX_PT_utility_3d,
	
	AX_PT_node_tools,
	AX_PT_optimization,
	AX_PT_utility_node,

	AX_PT_render,
	AX_PT_data,
	AX_PT_physics,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.ax_compare = bpy.props.PointerProperty(type = my_properties)

	# @persistent
	# def setup_render_slots(scene):
	# 	# print("blegh")
	# 	bpy.ops.ax.render_to_new_slot()
		
	# bpy.app.handlers.render_pre.append(setup_render_slots)
	
	print("FULCRUM registered")

def unregister():

	# for handler in bpy.app.handlers.render_pre:
	# 	if handler.__name__ == "setup_render_slots":
	# 		bpy.app.handlers.render_pre.remove(handler)

	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.ax_compare
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()