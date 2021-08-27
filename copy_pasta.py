import bpy
# from Tkinter import Tk

def to_clipboard(txt):
	# r = Tk()
	# r.withdraw()
	# r.clipboard_clear()
	# r.clipboard_append(txt)
	# r.update()
	# r.destroy()
	pass

def node_centroid(nodes):
	node_center = mathutils.Vector((0, 0))
	n = 0
	for node in nodes:
		if node.type == 'FRAME' or node.type == 'REROUTE':
			continue
		node_center += node.location + node.dimensions * mathutils.Vector((0.5, -0.5))
		# node_center += node.location + mathutils.Vector((0.5 * node.dimensions.x, - 0.5 * node.dimensions.y))
		n += 1
	return node_center / n


class AX_OT_copy_nodes(bpy.types.Operator):
	
	bl_idname = "ax.copy_nodes"
	bl_label = "Copy Nodes"
	bl_description = "Copy selected nodes to clipboard"
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):
		
		props_to_be_ignored = [
			"bl_description",
			"bl_height_default",
			"bl_height_max",
			"bl_height_min",
			"bl_icon",
			"bl_idname",
			"bl_label",
			"bl_static_type",
			"bl_width_default",
			"bl_width_max",
			"bl_width_min",
			"color",
			"dimensions",
			"height",
			"hide",
			"inputs",
			"internal_links",
			"is_active_output",
			"label",
			"location",
			"mute",
			"name",
			"outputs",
			"parent",
			"rna_type",
			"select",
			"show_options",
			"show_preview",
			"show_texture",
			"target",
			"type",
			"use_custom_color",
			"width",
			"width_hidden",
			"texture_mapping",
			"color_mapping",
			"interface"
		]
		
		tree = context.space_data.edit_tree
		# nodes = context.active_node.id_data.nodes
		nodes = context.selected_nodes
		links = [link for link in tree.links if link.from_node in nodes and link.to_node in nodes]

		centroid = node_centroid(nodes)

		for n, node in enumerate(nodes):
			
			node_type = node.bl_idname
			print(f"{node_type}\n")

			temp_node = tree.nodes.new(node_type)  # XXX ENDED HERE
			
			loc_x = int((node.location.x - centroid.x) / 10)
			loc_y = int((node.location.y - centroid.y) / 10)
			
			props = node.bl_rna.properties
			props = [prop for prop in props if not prop.is_readonly]
			print(f"ignored - {[prop.identifier for prop in props if prop.identifier in props_to_be_ignored]}\n")
			props = [prop for prop in props if prop.identifier not in props_to_be_ignored]
			
			for prop in props:
				print(f"{prop.identifier} = {getattr(node, prop.identifier)}")
			print("\n")

			# TODO node socket shader nema default value
			# TODO add new temp node to test defaults

			for input in node.inputs:
				if input.enabled:
					if not input.is_linked:
						print(f"{input.name} = {input.default_value}")
					else:
						print(f"{input.name} - ignored (is linked)")
				else:
					print(f"{input.name} - ignored (not enabled)")
			print("\n")

			for output in node.outputs:
				if output.enabled:
					if not output.is_linked:
						print(f"{output.name} = {output.default_value}")
						for channel in output.default_value:
							print(channel)
					else:
						print(f"{output.name} - ignored (is linked)")
				else:
					print(f"{output.name} - ignored (not enabled)")
			print("\n")
		

		for link in links:
			from_socket = link.from_socket
			to_socket = link.to_socket
			if from_socket.enabled and to_socket.enabled:
				from_socket = int(from_socket.path_from_id()[:-1].split("[")[-1])
				to_socket = int(to_socket.path_from_id()[:-1].split("[")[-1])
				print(f"{from_socket = }")
				print(f"{to_socket = }")
		
		to_clipboard()

		return {'FINISHED'}


class AX_OT_paste_nodes(bpy.types.Operator):
	
	bl_idname = "ax.paste_nodes"
	bl_label = "Paste Nodes"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = context.space_data.edit_tree.nodes

		for node in nodes:
			
			node_type = node.bl_idname
			
			node.location.x = loc_x * 10
			node.location.y = loc_y * 10

		return {'FINISHED'}