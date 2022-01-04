import bpy
import time
import os


class AX_OT_anim_time_limit(bpy.types.Operator):
	
	bl_idname = "ax.anim_time_limit"
	bl_label = "Animation Time Limit"
	bl_description = "Estimate samples so that render takes a certain time"
	COMPAT_ENGINES = {'CYCLES'}
	
	@classmethod
	def poll(cls, context):
		engine = context.scene.render.engine
		version_ok = bpy.app.version[0] >= 3
		return engine in cls.COMPAT_ENGINES and version_ok
	
	time_needed: bpy.props.FloatProperty(
		name = "Time",
		description = "How much time you want the render to take (in minutes)",
		unit = 'TIME_ABSOLUTE',
		step = 100,
		min = 0, default = 3600, soft_max = 86400
	)
	multiplier: bpy.props.FloatProperty(
		name = "Multiplier",
		description = "So there is some margin",
		soft_min = 0.0, default = 0.9, soft_max = 1.0
	)
	custom_range: bpy.props.BoolProperty(
		name = "Custom Range",
		description = "Otherwise use number of frames in scene",
		default = False
	)
	frames: bpy.props.IntProperty(
		name = "Custom Frame Range",
		description = "Custom number of frames",
		min = 1, default = 100
	)

	def execute(self, context):

		if self.custom_range:
			frames = self.frames
		else:
			start = context.scene.frame_start
			end = context.scene.frame_end
			step = context.scene.frame_step
			frames = (end - start + 1) // step

		time_limit = self.multiplier * self.time_needed / frames
		context.scene.cycles.time_limit = time_limit

		self.report({'INFO'}, f"Time Limit set to {time_limit} s")  # TODO round and use appropriate units
		return {'FINISHED'}

	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	
	def draw(self, context):
		
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		col = layout.column(align = True)
		col.prop(self, "time_needed")
		col.prop(self, "multiplier")

		heading = layout.column(align = True, heading = "Custom Frame Range")
		row = heading.row(align = True)
		row.prop(self, "custom_range", text = "")
		sub = row.row(align = True)
		sub.active = self.custom_range
		sub.prop(self, "frames", text = "")





# TODO clear empty slots

def check_if_render_slot_is_used(slot):

	tmp_path = os.path.join(bpy.path.abspath('//'), "tmp_img.png")

	try:
		bpy.data.images['Render Result'].save_render(filepath = tmp_path)
		# XXX probably only works for saved files ^
		return True
	except RuntimeError:
		return False
	
	# TODO delete test image ?
	os.remove(tmp_path)  # TODO delete only once at the end ?

class AX_OT_render_to_new_slot(bpy.types.Operator):

	bl_idname = "ax.render_to_new_slot"
	bl_label = "Render to New Slot"
	bl_description = "Render to Next Available Render Slot"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		render_result = bpy.data.images['Render Result']
		render_slots = render_result.render_slots

		render_slots.active = render_slots.new()
		render_slots.update()

		return {'FINISHED'}
	



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