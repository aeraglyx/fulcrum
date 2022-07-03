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

	combine_dir_ind: bpy.props.BoolProperty(
		name = "Combine Direct & Indirect",
		description = "",
		default = True
	)
	combine_light_color: bpy.props.BoolProperty(
		name = "Combine Light & Color",
		description = "",
		default = True
	)
	transparent: bpy.props.BoolProperty(
		name = "Transparent",
		description = "",
		default = True
	)

	diffuse: bpy.props.BoolProperty(
		name = "Diffuse",
		description = "",
		default = True
	)
	glossy: bpy.props.BoolProperty(
		name = "Glossy",
		description = "",
		default = True
	)
	transmission: bpy.props.BoolProperty(
		name = "Transmission",
		description = "",
		default = False
	)
	volume: bpy.props.BoolProperty(
		name = "Volume",
		description = "",
		default = False
	)
	emit: bpy.props.BoolProperty(
		name = "Emission",
		description = "",
		default = False
	)
	env: bpy.props.BoolProperty(
		name = "Environment",
		description = "",
		default = False
	)
	shadow: bpy.props.BoolProperty(
		name = "Shadow",
		description = "",
		default = False
	)
	ao: bpy.props.BoolProperty(
		name = "Ambient Occlusion",
		description = "",
		default = False
	)
	shadow_catcher: bpy.props.BoolProperty(
		name = "Shadow Catcher",
		description = "",
		default = False
	)

	z: bpy.props.BoolProperty(
		name = "Z",
		description = "",
		default = True
	)
	mist: bpy.props.BoolProperty(
		name = "Mist",
		description = "",
		default = True
	)
	position: bpy.props.BoolProperty(
		name = "Position",
		description = "",
		default = False
	)
	normal: bpy.props.BoolProperty(
		name = "Normal",
		description = "",
		default = False
	)
	vector: bpy.props.BoolProperty(
		name = "Vector",
		description = "",
		default = False
	)
	uv: bpy.props.BoolProperty(
		name = "UV",
		description = "",
		default = False
	)

	crypto_asset: bpy.props.BoolProperty(
		name = "Asset",
		description = "",
		default = False
	)
	crypto_material: bpy.props.BoolProperty(
		name = "Material",
		description = "",
		default = False
	)
	crypto_object: bpy.props.BoolProperty(
		name = "Object",
		description = "",
		default = False
	)


	def execute(self, context):

		context.scene.render.film_transparent = self.transparent
		
		def set_render_passes(view_layer):

			view_layer.use_pass_combined = True

			view_layer.use_pass_diffuse_color = self.diffuse
			view_layer.use_pass_diffuse_direct = self.diffuse
			view_layer.use_pass_diffuse_indirect = self.diffuse

			view_layer.use_pass_glossy_color = self.glossy
			view_layer.use_pass_glossy_direct = self.glossy
			view_layer.use_pass_glossy_indirect = self.glossy

			view_layer.use_pass_transmission_color = self.transmission
			view_layer.use_pass_transmission_direct = self.transmission
			view_layer.use_pass_transmission_indirect = self.transmission

			view_layer.use_pass_volume_direct = self.volume
			view_layer.use_pass_volume_indirect = self.volume

			view_layer.use_pass_emit = self.emit
			view_layer.use_pass_environment = self.env
			view_layer.use_pass_shadow = self.shadow
			view_layer.use_pass_ambient_occlusion = self.ao
			view_layer.use_pass_shadow_catcher = self.shadow_catcher

			view_layer.use_pass_z = self.z
			view_layer.use_pass_mist = self.mist
			view_layer.use_pass_position = self.position
			view_layer.use_pass_normal = self.normal
			view_layer.use_pass_vector = self.vector
			view_layer.use_pass_uv = self.uv

			view_layer.use_pass_cryptomatte_accurate = True
			view_layer.use_pass_cryptomatte_asset = self.crypto_asset
			view_layer.use_pass_cryptomatte_material = self.crypto_material
			view_layer.use_pass_cryptomatte_object = self.crypto_object

			view_layer.use_pass_object_index = False
			view_layer.use_pass_material_index = False

		bpy.context.scene.use_nodes = True
		nodes = context.scene.node_tree.nodes
		links = context.scene.node_tree.links

		view_layers = context.scene.view_layers
		for view_layer in view_layers:

			set_render_passes(view_layer)
			
			def plug_socket(socket, name):
				socket_a = output_node.layer_slots.new(name)
				links.new(socket, socket_a)
			
			def mix_nodes(socket_a, socket_b, mode):
				mix_node = nodes.new(type="CompositorNodeMixRGB")
				mix_node.blend_type = mode
				links.new(socket_a, mix_node.inputs[1])
				links.new(socket_b, mix_node.inputs[2])
				return mix_node.outputs[0]

			def make_link_1(input, output):
				socket_a = input_node.outputs[input]
				socket_b = output_node.layer_slots.new(output)
				links.new(socket_a, socket_b)
			
			def make_link_2(dir, ind, out):
				socket_dir = input_node.outputs[dir]
				socket_ind = input_node.outputs[ind]
				if self.combine_dir_ind:
					socket_light = mix_nodes(socket_dir, socket_ind, 'ADD')
					plug_socket(socket_light, out + "_light")
				else:
					plug_socket(socket_dir, out + "_dir")
					plug_socket(socket_ind, out + "_ind")

			def make_link_3(dir, ind, col, out):
				socket_dir = input_node.outputs[dir]
				socket_ind = input_node.outputs[ind]
				socket_col = input_node.outputs[col]
				if self.combine_dir_ind:
					socket_light = mix_nodes(socket_dir, socket_ind, 'ADD')
					if self.combine_light_color:
						socket_combined = mix_nodes(socket_light, socket_col, 'MULTIPLY')
						plug_socket(socket_combined, out)
					else:
						plug_socket(socket_light, out + "_light")
						plug_socket(socket_col, out + "_col")
				else:
					if self.combine_light_color:
						socket_dir = mix_nodes(socket_dir, socket_col, 'MULTIPLY')
						socket_ind = mix_nodes(socket_ind, socket_col, 'MULTIPLY')
						plug_socket(socket_dir, out + "_dir")
						plug_socket(socket_ind, out + "_ind")
					else:
						plug_socket(socket_dir, out + "_dir")
						plug_socket(socket_ind, out + "_ind")
						plug_socket(socket_col, out + "_col")

			input_node = nodes.new(type='CompositorNodesRLayers')
			context.scene.node_tree.nodes.active.layer = view_layer.name
		
			output_node = nodes.new(type='CompositorNodeOutputFile')
			output_node.format.file_format = 'OPEN_EXR'
			output_node.format.color_mode = 'RGBA' if self.transparent else 'RGB'
			output_node.format.color_depth = '32'
			output_node.format.exr_codec = 'NONE'
			
			output_node.layer_slots.clear()

			make_link_1('Image', 'rgba' if self.transparent else 'rgb')

			if self.diffuse:
				make_link_3('DiffDir', 'DiffInd', 'DiffCol', 'diff')
			if self.glossy:
				make_link_3('GlossDir', 'GlossInd', 'GlossCol', 'gloss')
			if self.transmission:
				make_link_3('TransDir', 'TransInd', 'TransCol', 'trans')
			if self.volume:
				make_link_2('VolumeDir', 'VolumeInd', 'trans')
			if self.emit:
				make_link_1('Emit', 'emit')
			if self.env:
				make_link_1('Env', 'env')
			if self.shadow:
				make_link_1('Shadow', 'shadow')
			if self.ao:
				make_link_1('AO', 'ao')
			if self.shadow_catcher:
				make_link_1('Shadow Catcher', 'shadow_catcher')
			
			if self.z:
				make_link_1('Depth', 'z')
			if self.mist:
				make_link_1('Mist', 'mist')
			if self.position:
				make_link_1('Position', 'position')
			if self.normal:
				make_link_1('Normal', 'normal')
			if self.vector:
				make_link_1('Vector', 'vector')
			if self.uv:
				make_link_1('UV', 'uv')
			

		return {'FINISHED'}

	def draw(self, context):

		layout = self.layout
		col = layout.column(align = True)
		
		col.prop(self, "combine_dir_ind")
		col.prop(self, "combine_light_color")
		col.prop(self, "transparent")
		
		col.prop(self, "diffuse")
		col.prop(self, "glossy")
		col.prop(self, "transmission")
		col.prop(self, "volume")
		col.prop(self, "emit")
		col.prop(self, "env")
		col.prop(self, "shadow")
		col.prop(self, "ao")
		col.prop(self, "shadow_catcher")
		
		col.prop(self, "z")
		col.prop(self, "mist")
		col.prop(self, "position")
		col.prop(self, "normal")
		col.prop(self, "vector")
		col.prop(self, "uv")

		col.prop(self, "crypto_asset")
		col.prop(self, "crypto_material")
		col.prop(self, "crypto_object")