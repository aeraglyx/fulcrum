import re
# import mathutils


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

def get_original_tree(tree, context):
	if tree.type == 'GEOMETRY':
		original_tree = context.object.modifiers.active.node_group
	if tree.type == 'SHADER':
		original_tree = context.material.node_tree
	# if tree.type == 'TEXTURE':
	# 	original_tree = context.
	if tree.type == 'COMPOSITING':
		original_tree = context.scene.node_tree
	return original_tree

def is_original_tree(tree, context):
	return get_original_tree(tree, context) == tree

def get_output_nodes(context):
	tree = context.space_data.edit_tree
	print(tree.type)
	nodes = tree.nodes
	if is_original_tree(tree, context):
		if tree.type == 'GEOMETRY':
			output_nodes = (node for node in nodes if node.bl_idname == 'NodeGroupOutput')  # bl_idname = 'GeometryNodeTree'
		if tree.type == 'SHADER':
			output_nodes = (node for node in nodes if node.bl_idname == 'ShaderNodeTree' and node.is_active_output == True)  # 'ShaderNodeTree'
		if tree.type == 'TEXTURE':
			output_nodes = (node for node in nodes if node.bl_idname == 'TextureNodeTree')  # doesn't have active outputs  # 'TextureNodeTree'
		if tree.type == 'COMPOSITING':  # 'COMPOSITE'
			output_nodes = (node for node in nodes if node.bl_idname == 'CompositorNodeTree')  # well yes but actually no ^  # 'CompositorNodeTree'
	else:
		output_nodes = (node for node in nodes if node.bl_idname == 'NodeGroupOutput')
	return output_nodes