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
				if tree.type == 'COMPOSITE':
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


class AX_OT_align_nodes(bpy.types.Operator):  # TODO

	# layered graph drawing
	
	bl_idname = "ax.align_nodes"
	bl_label = "Align Nodes"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = context.space_data.edit_tree.nodes
		selected = context.selected_nodes
		
		node.dimensions.y

		for input in (input for input in node_current.inputs if input.enabled):
			pass

		return {'FINISHED'}


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
		
		# bpy.ops.node.view_all()

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