import bpy

class AX_OT_dof_setup(bpy.types.Operator):

	bl_idname = "ax.dof_setup"
	bl_label = "DOF Setup"
	bl_description = "Add an empty and make it the active camera's Focus Object"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		# focus_obj = bpy.ops.object.empty_add()
		empty = bpy.data.objects.new("focus_empty", None)
		context.collection.objects.link(empty)

		print(empty.name)

		cam_obj = context.scene.camera
		cam_obj.data.dof.use_dof = True
		cam_obj.data.dof.focus_object = empty

		return {'FINISHED'}

