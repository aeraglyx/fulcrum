import bpy
import os
import subprocess

class AX_OT_open_script_dir(bpy.types.Operator):
	
	bl_idname = "ax.open_script_dir"
	bl_label = "Open Script Directory"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		path = bpy.utils.script_path_user()
		os.startfile(path)
		return {'FINISHED'}

class AX_OT_open_blend_dir(bpy.types.Operator):
	
	bl_idname = "ax.open_blend_dir"
	bl_label = "Open BLEND Directory"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bpy.data.is_saved

	def execute(self, context):
		# path = os.path.realpath(bpy.path.abspath("//"))  # XXX points to AHK dir when not saved
		path = bpy.data.filepath
		subprocess.Popen('explorer /select,"' + path + '"')
		return {'FINISHED'}