import bpy

class AX_OT_dof_setup(bpy.types.Operator):

	bl_idname = "ax.dof_setup"
	bl_label = "DOF Setup"
	bl_description = "Add an empty and make it the active camera's Focus Object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.scene.camera)

	alignment: bpy.props.FloatProperty(
		name = "Center / Cursor",
		description = "Center empty in camera's view or not",
		subtype = 'FACTOR',
		soft_min = 0.0, default = 1.0, soft_max = 1.0
	)

	def execute(self, context):

		camera_loc = context.scene.camera.location  # should be normalized
		cursor_loc = context.scene.cursor.location
		
		camera_vec = - bpy.context.scene.camera.matrix_world.to_3x3().transposed()[2]
		cursor_vec = cursor_loc - camera_loc

		center_loc = camera_loc + camera_vec * (camera_vec @ cursor_vec)
		empty_loc = (1 - self.alignment) * center_loc + self.alignment * cursor_loc

		cam_obj = context.scene.camera
		dof = cam_obj.data.dof
		dof.use_dof = True
		focus_obj = dof.focus_object
		
		if focus_obj and focus_obj.type == 'EMPTY':
			empty = focus_obj
		else:
			empty = bpy.data.objects.new("focus_empty", None)
			context.collection.objects.link(empty)

		dof.focus_object = empty
		empty.location = empty_loc

		for obj in bpy.data.objects:
			obj.select_set(state = False)
		
		empty.select_set(state = True)
		context.view_layer.objects.active = empty

		return {'FINISHED'}

	def draw(self, context):

		layout = self.layout
		col = layout.column(align = True)
		col.prop(self, "alignment")