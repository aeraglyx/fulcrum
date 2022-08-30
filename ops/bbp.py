import bpy

class AX_OT_edit_gn_input(bpy.types.Operator):
	
	bl_idname = "ax.edit_gn_input"
	bl_label = "Edit GN Input"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):

		obj = context.object		
		edit_id = obj.get('edit_id')

		def switch_mode(mode, tool):
			if obj.mode == mode:
				bpy.ops.object.mode_set(mode='OBJECT')
			else:
				bpy.ops.object.mode_set(mode=mode)
				bpy.ops.wm.tool_set_by_id(name=tool)
				# self.report({'INFO'}, f"scatter")

		match edit_id:
			case 'edit':
				switch_mode('EDIT', "builtin.select_box")
			case 'weight_paint':
				switch_mode('WEIGHT_PAINT', "builtin_brush.Draw")
			case 'draw_curve':
				switch_mode('EDIT', "builtin.draw")
			case _:
				switch_mode('EDIT', "builtin.select_box")
		
		return {'FINISHED'}