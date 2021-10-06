import bpy
import math
import mathutils

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
		soft_min = 0.0, default = 0.0, soft_max = 1.0  # TODO maybe default to center ?
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



class AX_OT_ortho_setup(bpy.types.Operator):

	bl_idname = "ax.ortho_setup"
	bl_label = "Orthographic Setup"
	bl_description = "Add an empty and make it the active camera's Focus Object"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.scene.camera)

	direction: bpy.props.EnumProperty(
		name = "Direction",
		description = "Which quadrant should the camera point to",
		items = [
			('0', "+X +Y", ""),
			('1', "-X +Y", ""),
			('2', "-X -Y", ""),
			('3', "+X -Y", "")
		],
		default = '3'
	)
	from_below: bpy.props.BoolProperty(
		name = "From Below",
		description = "Camera will be tilted upwards",
		default = False
	)
	distance: bpy.props.FloatProperty(
		name = "Distance",
		description = "How far from the center is the camera",
		soft_min = 0.0, default = 8.0, soft_max = 64
	)
	scale: bpy.props.FloatProperty(
		name = "Scale",
		description = "Orthographic Scale",
		min = 0.0, default = 8.0, soft_max = 16
	)

	def execute(self, context):

		cam_obj = context.scene.camera  # TODO new camera ?

		magic_angle = math.atan(math.sqrt(2))

		# euler = mathutils.Euler(mathutils.Vector((magic_angle, 0, - math.tau/8 )))
		# matrix_new = euler.to_matrix().to_4x4()
		# context.scene.camera.matrix_world = matrix_new

		dir_idx = int(self.direction)

		cam_obj.rotation_euler[0] = math.tau / 2 - magic_angle if self.from_below else magic_angle
		cam_obj.rotation_euler[1] = 0.0
		cam_obj.rotation_euler[2] = (2 * dir_idx + 3) * math.tau * 0.125

		if dir_idx == 0:
			y = 1.0
			x = 1.0
		elif dir_idx == 1:
			x = -1.0
			y = 1.0
		elif dir_idx == 2:
			x = -1.0
			y = -1.0
		elif dir_idx == 3:
			x = 1.0
			y = -1.0
		
		z = -1.0 if self.from_below else 1.0

		dist = self.distance
		cam_obj.location = dist * mathutils.Vector((x, y, z))

		cam_obj.data.type = 'ORTHO'
		cam_obj.data.ortho_scale = self.scale

		return {'FINISHED'}

	def draw(self, context):

		layout = self.layout

		row = layout.row()
		row.prop(self, "direction", expand = True)

		layout.prop(self, "from_below")

		col = layout.column(align = True)
		col.prop(self, "distance")
		col.prop(self, "scale")