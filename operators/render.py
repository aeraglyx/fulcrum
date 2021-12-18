import bpy

class AX_OT_set_render_passes(bpy.types.Operator):

	bl_idname = "ax.set_render_passes"
	bl_label = "Set Render Passes"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context):
	# 	return bool(context.scene.camera)

	combine_direct_indirect: bpy.props.BoolProperty(
		name = "Combine Direct & Indirect",
		description = "",
		default = False
	)
	combine_light_color: bpy.props.BoolProperty(
		name = "Combine Light & Color",
		description = "",
		default = False
	)


	def execute(self, context):
		
		def set_render_passes(view_layer):

			view_layer.use_pass_combined = True

			view_layer.use_pass_diffuse_color = True
			view_layer.use_pass_diffuse_direct = True
			view_layer.use_pass_diffuse_indirect = True

			view_layer.use_pass_glossy_color = True
			view_layer.use_pass_glossy_direct = True
			view_layer.use_pass_glossy_indirect = True

			view_layer.use_pass_subsurface_color = True
			view_layer.use_pass_subsurface_direct = True
			view_layer.use_pass_subsurface_indirect = True

			view_layer.use_pass_transmission_color = True
			view_layer.use_pass_transmission_direct = True
			view_layer.use_pass_transmission_indirect = True

			view_layer.use_pass_position = True
			view_layer.use_pass_z = True
			view_layer.use_pass_normal = True
			view_layer.use_pass_uv = True
			view_layer.use_pass_vector = True

			view_layer.use_pass_emit = True
			view_layer.use_pass_environment = True

			view_layer.use_pass_mist = False
			view_layer.use_pass_shadow = False
			use_pass_ambient_occlusion = False

			view_layer.use_pass_cryptomatte_accurate = True
			view_layer.use_pass_cryptomatte_asset = False
			view_layer.use_pass_cryptomatte_material = True
			view_layer.use_pass_cryptomatte_object = True

			view_layer.use_pass_object_index = False
			view_layer.use_pass_material_index = False

		bpy.context.scene.use_nodes = True

		view_layers = context.scene.view_layers
		for view_layer in view_layers:

			set_render_passes(view_layer)
			
			input_node = context.scene.node_tree.nodes.new(type = 'CompositorNodesRLayers')
			context.scene.node_tree.nodes.active.layer = view_layer.name
		
			output_node = context.scene.node_tree.nodes.new(type = 'CompositorNodeOutputFile')
			file_slots = output_node.file_slots
			file_slots.clear()
			for render_pass in render_passes:
				file_slots.new("")

		return {'FINISHED'}

	# def draw(self, context):

	# 	layout = self.layout
	# 	col = layout.column(align = True)
	# 	col.prop(self, "alignment")