import bpy
import os

# TODO clear empty slots

def check_if_render_slot_is_used(slot):

	tmp_path = os.path.join(bpy.path.abspath('//'), "tmp_img.png")

	try:
		bpy.data.images['Render Result'].save_render(filepath = tmp_path)
		# XXX probably only works for saved files ^
		return True
	except RuntimeError:
		return False
	
	# TODO delete test image ?
	os.remove(tmp_path)  # TODO delete only once at the end ?

class AX_OT_render_to_new_slot(bpy.types.Operator):

	bl_idname = "ax.render_to_new_slot"
	bl_label = "Render to New Slot"
	bl_description = "Render to Next Available Render Slot"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):

		render_result = bpy.data.images['Render Result']
		render_slots = render_result.render_slots

		render_slots.active = render_slots.new()
		render_slots.update()

		return {'FINISHED'}