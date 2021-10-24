import bpy
import string
import time
import datetime


def to62(x):
	letters = string.digits + string.ascii_lowercase + string.ascii_uppercase
	# letters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
	out = ""
	while x:
		m = x % 62
		x = x // 62
		out = letters[m] + out
	return out

def from62(x):
	letters = string.digits + string.ascii_lowercase + string.ascii_uppercase
	x = str(x)
	out = 0
	for i, char in enumerate(x):
		out += letters.find(char) * 62 ** (len(x) - i - 1)
	return out

def encode():
	x = int(time.time() // 60)
	x = to62(x)
	return x

def decode(x):
	x = from62(x) * 60
	x = datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d, %H:%M")
	return x

def has_version(name):
	if len(name) >= 8:
		format_ok = name[-6] == "#"
		alnum_ok = name[-5:].isalnum()
		date_ok = 1_600_000_000 < 60 * from62(name[-5:]) < 4_000_000_000
		has_version = format_ok and alnum_ok and date_ok
	else:
		has_version = False
	return has_version


class AX_OT_version_encode(bpy.types.Operator):
	
	bl_idname = "ax.version_encode"
	bl_label = "Encode Time"
	bl_description = "Append encoded time to the end of node group's name"
	
	@classmethod
	def poll(cls, context):
		if hasattr(context, "active_node"):
			node = context.active_node
			if node:
				return hasattr(node, "node_tree")
		return False

		# is_selected = context.active_node.select
		# return is_group and is_selected
		return is_group

	def execute(self, context):
		active = context.active_node
		name = active.node_tree.name
		version = encode()
		if has_version(name):
			new_name = name[:-5] + version
		else:
			new_name = name + "_#" + version
		active.node_tree.name = new_name
		return {'FINISHED'}


class AX_OT_version_decode(bpy.types.Operator):
	
	bl_idname = "ax.version_decode"
	bl_label = "Decode Time"
	bl_description = "Decode the time of last marked change"
	
	@classmethod
	def poll(cls, context):
		if hasattr(context, "active_node"):
			node = context.active_node
			if node:
				return hasattr(node, "node_tree")
		return False

	def execute(self, context):
		active = context.active_node
		name = active.node_tree.name
		date = decode(name[-5:])
		self.report({'INFO'}, f"{name[:-7]} | {name[-5:]} | {date}")
		return {'FINISHED'}