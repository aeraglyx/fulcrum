import bpy
import time


class AX_OT_anim_time_limit(bpy.types.Operator):
	
	bl_idname = "ax.anim_time_limit"
	bl_label = "Animation Time Limit"
	bl_description = "Estimate samples so that render takes a certain time"
	COMPAT_ENGINES = {'CYCLES'}
	
	@classmethod
	def poll(cls, context):
		engine = context.scene.render.engine
		version_ok = bpy.app.version[0] >= 3
		return engine in cls.COMPAT_ENGINES and version_ok
	
	time_needed: bpy.props.FloatProperty(
		name = "Time",
		description = "How much time you want the render to take (in minutes)",
		unit = 'TIME_ABSOLUTE',
		step = 100,
		min = 0, default = 3600, soft_max = 86400
	)
	multiplier: bpy.props.FloatProperty(
		name = "Multiplier",
		description = "So there is some margin",
		soft_min = 0.0, default = 0.9, soft_max = 1.0
	)
	custom_range: bpy.props.BoolProperty(
		name = "Custom Range",
		description = "Otherwise use number of frames in scene",
		default = False
	)
	frames: bpy.props.IntProperty(
		name = "Custom Frame Range",
		description = "Custom number of frames",
		min = 1, default = 100
	)

	def execute(self, context):

		if self.custom_range:
			frames = self.frames
		else:
			start = context.scene.frame_start
			end = context.scene.frame_end
			step = context.scene.frame_step
			frames = (end - start + 1) // step

		time_limit = self.multiplier * self.time_needed / frames
		context.scene.cycles.time_limit = time_limit

		self.report({'INFO'}, f"Time Limit set to {time_limit} s")  # TODO round and use appropriate units
		return {'FINISHED'}

	def invoke(self, context, event):

		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	
	def draw(self, context):
		
		layout = self.layout
		layout.use_property_split = True
		layout.use_property_decorate = False

		col = layout.column(align = True)
		col.prop(self, "time_needed")
		col.prop(self, "multiplier")

		heading = layout.column(align = True, heading = "Custom Frame Range")
		row = heading.row(align = True)
		row.prop(self, "custom_range", text = "")
		sub = row.row(align = True)
		sub.active = self.custom_range
		sub.prop(self, "frames", text = "")