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

	
	# index: bpy.props.IntProperty(
	# 	name = "Index",
	# 	min = 0, default = 0
	# )

	def execute(self, context):

		render_result = bpy.data.images['Render Result']
		slots = render_result.render_slots

		number_of_slots = len(slots)
		unused_slot_indices = []

		for i in range(number_of_slots):
			
			slots.active_index = i
			slot = slots.active
			slot_used = check_if_render_slot_is_used(slot)
			# print(f"Slot \"{slot.name}\" is {'used' if slot_used else 'unused'}.")
			
			if not slot_used:
				unused_slot_indices.append(i)
		
		unused_slot_indices.reverse()




		prev_editor_type = bpy.context.area.type
		bpy.context.area.ui_type = 'IMAGE_EDITOR'
		bpy.context.area.spaces.active.image = render_result



		# override = bpy.context.copy()
		# override['area']['ui_type'] = 'IMAGE_EDITOR'
		# override['area']['spaces']['active']['image'] = render_result





		for i in unused_slot_indices:
			slots.active_index = i
			bpy.ops.image.remove_render_slot()
			# bpy.ops.image.remove_render_slot(override)
		
		bpy.ops.image.add_render_slot()
		# bpy.ops.image.add_render_slot(override)
		# slots.active.name = "kldsf"
		bpy.context.area.ui_type = prev_editor_type

		# bpy.ops.render.render()

		return {'FINISHED'}