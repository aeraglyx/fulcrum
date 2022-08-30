bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 4, 0),
	"version": (0, 1, 13),
	"location": "Everywhere",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy
# from bpy.app.handlers import persistent

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
from .ops.bbp import AX_OT_edit_gn_input
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
	AX_PT_bbp,
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
	AX_PT_bbp,
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

	AX_OT_edit_gn_input,
)

addon_keymaps = []


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.ax_compare = bpy.props.PointerProperty(type = my_properties)

	# https://github.com/aachman98/Sorcar/blob/master/__init__.py#L113
	# wm = bpy.context.window_manager
	# kc = wm.keyconfigs.addon
	# if kc:
	# 	km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
	# 	kmi = km.keymap_items.new("ax.edit_gn_input", type='SPACE', value='PRESS', alt=True)
	# 	addon_keymaps.append((km, kmi))
	
	kc = bpy.context.window_manager.keyconfigs.addon
	if kc:
		km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
		kmi = km.keymap_items.new('ax.edit_gn_input', 'SPACE', 'PRESS', alt=True)
		addon_keymaps.append((km, kmi))
	
	print("FULCRUM registered")

def unregister():

	for km, kmi in addon_keymaps:
		km.keymap_items.remove(kmi)
	addon_keymaps.clear()

	# kc = bpy.context.window_manager.keyconfigs.addon
	# if kc:
	# 	km = kc.keymaps["3D View"]
	# 	for kmi in km.keymap_items:
	# 		if kmi.idname == 'ax.edit_gn_input':
	# 			km.keymap_items.remove(kmi)
	# 			break

	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.ax_compare
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()