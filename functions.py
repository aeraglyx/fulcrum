import re
import math
import mathutils

def oklab_2_srgb(l, a, b):
	# https://bottosson.github.io/posts/oklab/

	x = l + 0.3963377774 * a + 0.2158037573 * b
	y = l - 0.1055613458 * a - 0.0638541728 * b
	z = l - 0.0894841775 * a - 1.2914855480 * b

	x = x * x * x
	y = y * y * y
	z = z * z * z

	return [
		+4.0767416621 * x - 3.3077115913 * y + 0.2309699292 * z,
		-1.2684380046 * x + 2.6097574011 * y - 0.3413193965 * z,
		-0.0041960863 * x - 0.7034186147 * y + 1.7076147010 * z
	]

def oklab_hsl_2_srgb(h, s, l):
	""" HSL but based on Oklab, so better :) """
	# https://bottosson.github.io/posts/oklab/

	a = s * math.cos(h * math.tau)
	b = s * math.sin(h * math.tau)

	x = l + 0.3963377774 * a + 0.2158037573 * b
	y = l - 0.1055613458 * a - 0.0638541728 * b
	z = l - 0.0894841775 * a - 1.2914855480 * b

	x = x * x * x
	y = y * y * y
	z = z * z * z

	return [
		+4.0767416621 * x - 3.3077115913 * y + 0.2309699292 * z,
		-1.2684380046 * x + 2.6097574011 * y - 0.3413193965 * z,
		-0.0041960863 * x - 0.7034186147 * y + 1.7076147010 * z
	]

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
	if node.label:
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
	if node.hide == True:
		return 32
	return node.dimensions[1] * node.width / node.dimensions[0]

def node_size(node):
	if node.type == 'REROUTE':
		return mathutils.Vector((0, 0))
	x = node.width
	y = node.dimensions[1] * node.width / node.dimensions[0]
	return mathutils.Vector((x, y))
	
def node_center(node):
	return node.location + node_size(node) * mathutils.Vector((0.5, -0.5))

def node_intersection(node_1, node_2):
	x = 20
	y = 20
	lx = max(node_1.location.x - x, node_2.location.x - x)
	rx = min(node_1.location.x + node_width(node_1) + x, node_2.location.x + node_width(node_2) + x)
	if lx > rx:
		return None
	uy = min(node_1.location.y + y, node_2.location.y + y)
	dy = max(node_1.location.y - node_height(node_1) - y, node_2.location.y - node_height(node_2) - y)
	if uy < dy:
		return None
	return (mathutils.Vector((lx, dy)), mathutils.Vector((rx - lx, uy - dy)))

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
				out = mathutils.Vector((x, y))
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
				out = mathutils.Vector((x, y))
			y += Y_OFFSET + VEC_TOP * tall
	
	return out

def get_original_tree(tree, context):
	if tree.type == 'GEOMETRY':
		original_tree = context.object.modifiers.active.node_group
	if tree.type == 'SHADER':
		if context.space_data.shader_type == 'OBJECT':
			original_tree = context.material.node_tree
		if context.space_data.shader_type == 'WORLD':
			original_tree = context.scene.world.node_tree
		if context.space_data.shader_type == 'LINESTYLE':
			pass  # TODO
	if tree.type == 'COMPOSITING':
		original_tree = context.scene.node_tree
	# if tree.type == 'TEXTURE':
	# 	original_tree = context.
	return original_tree

def is_original_tree(tree, context):
	return get_original_tree(tree, context) == tree

def is_node_group(tree):
	# tree.inputs
	# return get_original_tree(tree, context) != tree
	return tree in bpy.data.node_groups

def get_output_nodes(context):
	tree = context.space_data.edit_tree
	nodes = tree.nodes
	if is_original_tree(tree, context):
		if tree.type == 'GEOMETRY':
			output_nodes = (node for node in nodes if node.bl_idname == 'NodeGroupOutput')  # bl_idname = 'GeometryNodeTree'
		if tree.type == 'SHADER':
			output_nodes = (node for node in nodes if node.bl_idname in ['ShaderNodeTree', 'ShaderNodeOutputWorld'] and node.is_active_output == True)  # 'ShaderNodeTree'
		if tree.type == 'TEXTURE':
			output_nodes = (node for node in nodes if node.bl_idname == 'TextureNodeTree')  # doesn't have active outputs  # 'TextureNodeTree'
		if tree.type == 'COMPOSITING':  # 'COMPOSITE'
			output_nodes = (node for node in nodes if node.bl_idname in ['CompositorNodeTree', 'CompositorNodeOutputFile'])  # well yes but actually no ^  # 'CompositorNodeTree'
	else:
		output_nodes = (node for node in nodes if node.bl_idname == 'NodeGroupOutput')
	return output_nodes

def version_up(name):
	# if it doesn't have a version, add it
	if not name[-1].isdigit():
		return name + "_v02"  # v001 or v002 ?
	# otherwise increment by 1
	old_name = re.sub("\d+$", "", name)
	old_v = re.search("\d+$", name).group()
	new_v = str(int(old_v) + 1).zfill(len(old_v))
	return old_name + new_v

import addon_utils
def get_addon_version(addon_name):
	version = [addon.bl_info.get('version', (-1,-1,-1)) for addon in addon_utils.modules() if addon.bl_info['name'] == addon_name][0]
	return ".".join(map(str, version))