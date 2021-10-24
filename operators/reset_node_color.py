import bpy

class AX_OT_reset_node_color(bpy.types.Operator):
	
	""" Reset custom node color """
	
	bl_idname = "ax.reset_node_color"
	bl_label = "Reset Node Color"
	bl_description = "Reset custom node color"

	all: bpy.props.BoolProperty(
		name = "All",
		description = "Reset color for all nodes, not just selected",
		default = False
	)
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'NODE_EDITOR'

	def execute(self, context):
		
		if self.all == True:
			nodes = context.space_data.edit_tree.nodes  # context.active_node.id_data.nodes
			for node in nodes:
				node.use_custom_color = False
		else:
			selected = context.selected_nodes
			for node in selected:
				node.use_custom_color = False
		
		return {'FINISHED'}