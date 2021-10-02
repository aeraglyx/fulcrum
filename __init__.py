bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (3, 0, 0),
	"version": (0, 1, 6),
	"location": "Everywhere",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy
from bpy.app.handlers import persistent

from . compare import AX_OT_compare, my_properties, AX_OT_benchmark
from . reset_node_color import AX_OT_reset_node_color
from . render_in_time import AX_OT_render_in_time
from . vert_group_2_col import AX_OT_vert_group_2_col
from . paint import AX_OT_set_paint_brush, AX_OT_set_weight_brush
from . node_flow import AX_OT_node_flow, AX_OT_unused_nodes, AX_OT_find_inputs, AX_OT_center_nodes, AX_OT_nodes_to_grid
from . versioning import AX_OT_version_encode, AX_OT_version_decode
from . utility import AX_OT_locate_vertex, AX_OT_locate_vertices
from . copy_pasta import AX_OT_copy_nodes, AX_OT_paste_nodes
from . render_slots import AX_OT_render_to_new_slot

from . ui import (
	AX_PT_optimization, AX_PT_node_tools, AX_PT_utility_node,
	AX_PT_render, AX_PT_data,
	AX_PT_paint, AX_PT_utility_3d
)

classes = (
	my_properties,
	
	AX_OT_reset_node_color, AX_OT_compare, AX_OT_benchmark,
	AX_OT_render_in_time, AX_OT_vert_group_2_col,
	AX_OT_set_paint_brush, AX_OT_set_weight_brush,
	AX_OT_locate_vertex, AX_OT_locate_vertices,
	
	AX_PT_node_tools, AX_PT_optimization, AX_PT_utility_node,
	AX_PT_render, AX_PT_data,
	AX_PT_paint, AX_PT_utility_3d,
	AX_OT_node_flow, AX_OT_unused_nodes, AX_OT_find_inputs, AX_OT_center_nodes, AX_OT_nodes_to_grid,
	AX_OT_version_encode, AX_OT_version_decode,
	AX_OT_copy_nodes, AX_OT_paste_nodes,

	AX_OT_render_to_new_slot
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.ax_compare = bpy.props.PointerProperty(type = my_properties)

	@persistent
	def setup_render_slots(scene):
		# print("blegh")
		bpy.ops.ax.render_to_new_slot()

	bpy.app.handlers.render_pre.append(setup_render_slots)
	
	print("FULCRUM registered")

def unregister():

	# bpy.app.handlers.render_pre.remove(setup_render_slots)  # XXX check this !

	for handler in bpy.app.handlers.render_pre:
		if handler.__name__ == "render_to_new_slot":
			bpy.app.handlers.render_pre.remove(handler)

	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.ax_compare
	
	print("FULCRUM unregistered")

if __name__ == "__main__":
	register()