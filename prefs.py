import bpy

class FulcrumPreferences(bpy.types.AddonPreferences):
	
	bl_idname = __package__

	experimental: bpy.props.BoolProperty(
		name='Unlimited Power',
		default=False,
	)
	# restart_needed: bpy.props.BoolProperty(
	# 	name='Restart Needed',
	# 	default=False,
	# 	options={'SKIP_SAVE'}
	# )
 
	def draw(self, context):
		
		layout = self.layout
		layout.prop(self, 'experimental')
		
		layout.operator("fulcrum.update_fulcrum", text="Update", icon='FILE_REFRESH')
		if context.scene.fulcrum.restart_needed:
			layout.label(text="Updated. Blender needs restarting.", icon='SEQUENCE_COLOR_07')