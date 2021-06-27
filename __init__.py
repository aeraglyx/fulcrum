bl_info = {
	"name": "Fulcrum",
	"author": "Vladislav Macíček (Aeraglyx)",
	"description": "All kinds of tools",
	"blender": (2, 93, 0),
	"version": (0, 1, 5),
	"location": "Everywhere",
	"doc_url": "https://github.com/aeraglyx/fulcrum",
	"category": 'User Interface',
	"support": 'COMMUNITY'
}

import bpy

from . compare import AX_OT_compare, my_properties, AX_OT_benchmark
from . reset_node_color import AX_OT_reset_node_color
from . render_in_time import AX_OT_render_in_time
from . vert_group_2_col import AX_OT_vert_group_2_col
from . paint import AX_OT_set_paint_brush, AX_OT_set_weight_brush
from . node_flow import AX_OT_node_flow, AX_OT_unused_nodes, AX_OT_find_inputs
from . versioning import AX_OT_version_encode, AX_OT_version_decode

from . ui import (
	AX_PT_optimization, AX_PT_node_tools, AX_PT_utility,
	AX_PT_render, AX_PT_data,
	AX_PT_paint
)

classes = (
	my_properties,
	
	AX_OT_reset_node_color, AX_OT_compare, AX_OT_benchmark,
	AX_OT_render_in_time, AX_OT_vert_group_2_col,
	AX_OT_set_paint_brush, AX_OT_set_weight_brush,
	
	AX_PT_node_tools, AX_PT_optimization, AX_PT_utility,
	AX_PT_render, AX_PT_data,
	AX_PT_paint,
	AX_OT_node_flow, AX_OT_unused_nodes, AX_OT_find_inputs,
	AX_OT_version_encode, AX_OT_version_decode
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.Scene.ax_compare = bpy.props.PointerProperty(type = my_properties)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	del bpy.types.Scene.ax_compare

if __name__ == "__main__":
	register()