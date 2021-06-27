import bpy

class AX_OT_vert_group_2_col(bpy.types.Operator):
	
	bl_idname = "ax.vert_group_2_col"
	bl_label = "Groups to Colors"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return len(bpy.context.active_object.vertex_groups) # HACK idk

	def execute(self, context):

		groups = bpy.context.active_object.vertex_groups
		colors = bpy.context.active_object.data.vertex_colors

		need_to_switch_back = False
		if bpy.context.mode != 'PAINT_VERTEX':
			bpy.ops.paint.vertex_paint_toggle()
			need_to_switch_back = True

		for group in groups:

			# FIXME max 8 vert. colours
			
			col = colors.new()
			col.name = group.name

			groups.active = group
			colors.active = col

			bpy.ops.paint.vertex_color_from_weight()  # FIXME probably does not work for "empty" groups (new ones)

		if need_to_switch_back:
			bpy.ops.paint.vertex_paint_toggle()

		self.report({'INFO'}, f"Done.")

		return {'FINISHED'}