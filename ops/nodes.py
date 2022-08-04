import bpy
import re
import mathutils


def color_nodes(nodes, color):
	for node in nodes:
		node.use_custom_color = True
		node.color = color

def clear_node_color(nodes):
	for node in nodes:
		node.use_custom_color = False

def get_node_name(node):
	"""Get node name that is visible to user"""
	# label > prop. name > name
	if bool(node.label):
		return node.label
	elif hasattr(node, "node_tree"):
		return node.node_tree.name
	else:
		name = node.name
		return re.sub(".[0-9]{3,}$", "", name) # XXX {3} or {3,}

def node_width(node):
	if node.type == 'REROUTE':
		return 0
	return node.width

def node_height(node):
	if node.type == 'REROUTE':
		return 0
	return node.dimensions[1] * node.width / node.dimensions[0]

def socket_loc(socket):
	X_OFFSET = -1.0
	Y_TOP = -34.0
	Y_BOTTOM = 16.0
	Y_OFFSET = 22.0

	# 2 offsets 
	VEC_BOTTOM = 28.0
	VEC_TOP = 32.0

	def is_tall(socket):
		if socket.type != 'VECTOR':
			return False
		if socket.hide_value:
			return False
		if socket.is_linked:
			return False
		# if socket.node.type == 'BSDF_PRINCIPLED' and socket.identifier == 'Subsurface Radius':
		# 	return False  # an exception confirms a rule?
		return True
	
	node = socket.node
	if socket.is_output:
		x = node.location.x + node_width(node) + X_OFFSET
		y = node.location.y + Y_TOP    
		for output in node.outputs:
			if output.hide or not output.enabled:
				continue
			if output == socket:
				out = [x, y]
			y -= Y_OFFSET
	else:
		x = node.location.x
		y = node.location.y - node_height(node) + Y_BOTTOM
		for input in reversed(node.inputs):
			if input.hide or not input.enabled:
				continue
			tall = is_tall(input)
			y += VEC_BOTTOM * tall
			if input == socket:
				out = [x, y]
			y += Y_OFFSET + VEC_TOP * tall
	
	return out


class AX_OT_find_inputs(bpy.types.Operator):
	
	bl_idname = "ax.find_inputs"
	bl_label = "Find Inputs"
	bl_description = "Show all nodes used by the selected nodes"
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = bpy.context.space_data.edit_tree.nodes
		selected = context.selected_nodes

		clear_node_color(nodes)
		
		nodes_out = []
		def get_input_node(input):
			for link in input.links:
				node = link.from_node
				if node.type == 'REROUTE':
					get_input_node(node.inputs[0])
				elif not node.mute:
					nodes_out.append(node)
		
		for node_orig in selected:
			for input in (x for x in node_orig.inputs if x.enabled):
				get_input_node(input)

		color_nodes(nodes_out, [0.3, 0.6, 0.3])
		
		return {'FINISHED'}

class AX_OT_node_flow(bpy.types.Operator):
	
	bl_idname = "ax.node_flow"
	bl_label = "Dependencies"
	bl_description = "Show all nodes used by the selected nodes"
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = bpy.context.space_data.edit_tree.nodes
		selected = context.selected_nodes
		
		clear_node_color(nodes)

		nodes_out = []
		def func(node_current):
			for input in (x for x in node_current.inputs if x.enabled):
				for link in input.links: # TODO links plural ? link limit
					node = link.from_node
					if node not in nodes_out:
						nodes_out.append(node)
						func(node)
		
		for node in selected:
			func(node)
		
		color_nodes(nodes_out, [0.2, 0.45, 0.6])

		return {'FINISHED'}

class AX_OT_unused_nodes(bpy.types.Operator):
	
	bl_idname = "ax.unused_nodes"
	bl_label = "Unused Nodes"
	bl_description = "Show all nodes used by the selected nodes"
	
	# @classmethod
	# def poll(cls, context):
	#     return bool(context.selected_nodes)

	# TODO make it work for inside of node groups

	def execute(self, context):

		tree = context.space_data.edit_tree  # context.active_node.id_data
		nodes = tree.nodes
		# output_node = nodes.get("Material Output")
		def is_original_tree(tree):
			return context.material.node_tree == tree  # XXX bruh

		def get_output_nodes(tree):
			if is_original_tree(tree):
				if tree.type == 'GEOMETRY':
					return (node for node in nodes if node.bl_idname == 'GeometryNodeTree')  # bl_idname = 'GeometryNodeTree'
				if tree.type == 'SHADER':
					return (node for node in nodes if node.bl_idname == 'ShaderNodeTree' and node.is_active_output == True)  # 'ShaderNodeTree'
				if tree.type == 'TEXTURE':
					return (node for node in nodes if node.bl_idname == 'TextureNodeTree')  # doesn't have active outputs  # 'TextureNodeTree'
				if tree.type == 'COMPOSITING':  # 'COMPOSITE'
					return (node for node in nodes if node.bl_idname == 'CompositorNodeTree')  # well yes but actually no ^  # 'CompositorNodeTree'
			else:
				return (node for node in nodes if node.bl_idname == 'NodeGroupOutput')
		
		clear_node_color(nodes)

		used = set()
		def func(node_current):
			used.add(node_current)
			used.add(node_current.parent)
			for input in (x for x in node_current.inputs if x.enabled):  # TODO muted nodes and muted links
				for link in input.links:
					func(link.from_node)
		
		output_nodes = get_output_nodes(tree)
		for output_node in output_nodes:
			func(output_node)
		
		# TODO don't delete viewer (geo, shader, ...) - check if connected to used node, otherwise yeet
		unused = [node for node in nodes if node not in used]

		color_nodes(unused, [0.65, 0.29, 0.32])

		return {'FINISHED'}

class AX_OT_align_nodes(bpy.types.Operator):

	# layered graph drawing
	
	bl_idname = "ax.align_nodes"
	bl_label = "Align Nodes"
	bl_description = "Automatically align all the nodes preceding the selection"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")
	
	test: bpy.props.FloatProperty(
		name = "Test",
		description = "Number of total subdivisions",
		soft_min = 0.0, default = 0.25, soft_max = 8.0,
	)
	spacing: bpy.props.IntVectorProperty(
		name = "Spacing",
		description = "Spacing between nodes",
		min = 0, default = (40, 20), soft_max = 100,
		size = 2
	)

	def execute(self, context):
		# if node_tree.type == 'COMPOSITING':
		# 	nodes = context.scene.node_tree.nodes
		print(context.space_data)
		print(context.space_data.type)

		nodes = context.space_data.edit_tree.nodes  # BUG doesn't work in compositor
		# bpy.context.space_data.edit_tree
		# nodes = context.active_node.id_data.nodes
		levels = {node:0 for node in nodes}

		def figure_out_levels(node_current, level_current):
			inputs = (x for x in node_current.inputs if x.enabled)
			for input in inputs:
				for link in input.links:
					node = link.from_node
					if levels[node] <= level_current:
						levels[node] = level_current + 1
						figure_out_levels(node, level_current + 1)
		
		root_node = context.active_node
		figure_out_levels(root_node, 0)
		
		level_current = 1
		x = 0
		while True:
			nodes = [node for (node, level) in levels.items() if level == level_current]
			if not nodes:
				break
			orders = []
			for node in nodes:
				node.select = True
				weight_total = 0.0
				pos_thingy = 0.0
				outputs = (x for x in node.outputs if x.enabled and not x.hide)
				for output in outputs:
					links = (x for x in output.links if x.to_socket.enabled and not x.to_socket.hide)
					for link in links:  # [link for link in output.links if link.to_socket.enabled or not link.to_socket.hide]
						level_diff = level_current - levels[link.to_node]
						weight = 2 ** (self.test * (1 - level_diff))
						weight_total += weight
						pos_thingy += socket_loc(link.to_socket)[1] * weight
				orders.append(pos_thingy / weight_total)
			nodes = [node for _, node in sorted(zip(orders, nodes), key=lambda x: x[0], reverse=True)]
			spacing_y = self.spacing[1]
			full_height = sum([node_height(node) for node in nodes]) + spacing_y * (len(nodes) - 1)
			x -= max([node_width(node) for node in nodes]) + self.spacing[0]
			y = full_height * 0.5
			for node in nodes:
				node.location = [x, y]
				y -= node_height(node) + spacing_y
			level_current += 1

		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False
		# col = layout.column(align = True)
		layout.prop(self, "spacing")
		layout.prop(self, "test")

class AX_OT_nodes_to_grid(bpy.types.Operator):
	
	bl_idname = "ax.nodes_to_grid"
	bl_label = "Nodes to Grid"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):
		selected = context.selected_nodes
		for node in selected:
			node.location.x = int(node.location.x / 10) * 10
			node.location.y = int(node.location.y / 10) * 10
		return {'FINISHED'}

class AX_OT_center_nodes(bpy.types.Operator):
	
	bl_idname = "ax.center_nodes"
	bl_label = "Center Nodes"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = context.space_data.edit_tree.nodes
		# FIXME takes nodes inside groups as well (does it?)

		node_center = mathutils.Vector((0, 0))
		n = 0
		for node in nodes:
			if node.type == 'FRAME' or node.type == 'REROUTE':
				continue
			node_center += node.location + node.dimensions * mathutils.Vector((0.5, -0.5))
			n += 1
		
		node_center /= n

		for node in nodes:
			if node.type == 'FRAME':  # TODO move frames, not their children
				continue
			node.location -= node_center
		
		bpy.ops.node.view_all()

		return {'FINISHED'}

class AX_OT_add_todo_note(bpy.types.Operator):
	
	bl_idname = "ax.add_todo_note"
	bl_label = "Add TODO Note"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")
	
	note: bpy.props.StringProperty(
		name = "Note",
		default = "",
	)

	def execute(self, context):

		nodes = context.space_data.edit_tree.nodes

		todo_node = nodes.new(type = 'NodeFrame')
		todo_node.label = self.note
		todo_node.width = 400
		todo_node.height = 100
		# bpy.ops.node.add_search(use_transform=True, node_item='92')

		# TODO WIP
		
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	
	def draw(self, context):
		
		layout = self.layout
		# layout.use_property_split = True
		# layout.use_property_decorate = False

		col = layout.column(align = True)
		col.prop(self, "note")

class AX_OT_hide_group_inputs(bpy.types.Operator):
	
	bl_idname = "ax.hide_group_inputs"
	bl_label = "Hide Group Inputs"
	bl_description = ""
	
	# @classmethod
	# def poll(cls, context):
	# 	return hasattr(context, "selected_nodes")

	def execute(self, context):
		nodes = context.space_data.edit_tree.nodes
		print(context.space_data.edit_tree.name)
		for node in nodes:
			if node.type == 'GROUP_INPUT':
				for socket in node.outputs:
					if socket.enabled and not socket.is_linked:
						socket.hide = True
		return {'FINISHED'}

class AX_OT_tex_to_name(bpy.types.Operator):
	
	bl_idname = "ax.tex_to_name"
	bl_label = "Tex > Mat Name"
	bl_description = "Name material or object after image used by the active Image Texture node"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		if context.area.ui_type == 'ShaderNodeTree':
			if context.space_data.shader_type == 'OBJECT':
				if hasattr(context, "active_node"):
					node = context.active_node
					if node and node.select and node.type == 'TEX_IMAGE':
						return bool(node.image)
		return False
	
	mat: bpy.props.BoolProperty(
		name = "Material",
		description = "xxx",
		default = True)
	obj: bpy.props.BoolProperty(
		name = "Object",
		description = "xxx",
		default = True)

	def execute(self, context):
		node = context.active_node	
		img_name = ".".join(node.image.name.split(".")[:-1])
		if self.mat:
			context.material.name = img_name
		if self.obj:
			context.object.name = img_name
		return {'FINISHED'}
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False
		layout.prop(self, "mat")
		layout.prop(self, "obj")

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

class AX_OT_set_gn_defaults(bpy.types.Operator):
	
	bl_idname = "ax.set_gn_defaults"
	bl_label = "Set GN Defaults"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'NODE_EDITOR'

	def execute(self, context):

		# group = context.space_data.edit_tree
		modif = context.object.modifiers.active
		group = modif.node_group

		for input in group.inputs[1:]:
			if input.default_value:
				input.default_value = modif[input.identifier]
		
		return {'FINISHED'}

class AX_OT_reset_gn_defaults(bpy.types.Operator):
	
	bl_idname = "ax.reset_gn_defaults"
	bl_label = "Reset GN Defaults"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return context.area.type == 'NODE_EDITOR'

	def execute(self, context):

		# group = context.space_data.edit_tree
		modif = context.object.modifiers.active
		group = modif.node_group

		for input in group.inputs[1:]:
			if input.default_value:
				modif[input.identifier] = input.default_value
		
		return {'FINISHED'}