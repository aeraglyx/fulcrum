import bpy

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
		
		# nodes = context.active_node.id_data.nodes
		nodes = context.selected_nodes

		for node in nodes:
			
			node_type = node.bl_idname
			print(f"{node_type}\n")
			# location = int(D.materials['Material'].node_tree.nodes.active.location.x / 8) * 8
			
			props = node.bl_rna.properties
			props = [prop for prop in props if not prop.is_readonly]
			print(f"ignored - {[prop.identifier for prop in props if prop.identifier in props_to_be_ignored]}\n")
			props = [prop for prop in props if prop.identifier not in props_to_be_ignored]
			

			for prop in props:
				print(f"{prop.identifier} = {getattr(node, prop.identifier)}")
			print("\n")

			for input in node.inputs:
					
				if input.enabled:
					if not input.is_linked:
						print(f"{input.name} = {input.default_value}")
					else:
						print(f"{input.name} - ignored (is linked)")
				else:
					print(f"{input.name} - ignored (not enabled)")

			print("\n")

		return {'FINISHED'}


class AX_OT_paste_nodes(bpy.types.Operator):
	
	bl_idname = "ax.paste_nodes"
	bl_label = "Paste Nodes"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return hasattr(context, "selected_nodes")

	def execute(self, context):

		nodes = context.active_node.id_data.nodes

		for node in nodes:
			node_type = node.bl_idname

		return {'FINISHED'}