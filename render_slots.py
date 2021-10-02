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

class AX_OT_render_to_next_slot(bpy.types.Operator):

	bl_idname = "ax.render_to_next_slot"
	bl_label = "Render to Next Slot"
	bl_description = "Render to Next Available Render Slot"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		# return context.active_object
		return True
	
	# index: bpy.props.IntProperty(
	# 	name = "Index",
	# 	min = 0, default = 0
	# )

	def execute(self, context):

		# bpy.data.images["Render Result"].(null) = 0


		# TODO set active slot

		# render_result = 
		render_result = bpy.data.images['Render Result']
		slots = render_result.render_slots

		number_of_slots = len(slots)
		unused_slot_indices = []

		for i in range(number_of_slots):
			
			slots.active_index = i
			slot = slots.active
			slot_used = check_if_render_slot_is_used(slot)
			print(f"Slot \"{slot.name}\" is {'used' if slot_used else 'unused'}.")
			
			if not slot_used:
				unused_slot_indices.append(i)
		
		unused_slot_indices.reverse()
		prev_editor_type = bpy.context.area.type
		bpy.context.area.ui_type = 'IMAGE_EDITOR'
		bpy.context.area.spaces.active.image = render_result
		for i in unused_slot_indices:
			slots.active_index = i
			bpy.ops.image.remove_render_slot()
			# print(f"jakoze mazu slot #{i}")
		bpy.context.area.ui_type = prev_editor_type



		


		return {'FINISHED'}
	
	# def invoke(self, context, event):
	# 	wm = context.window_manager
	# 	return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "index")