import bpy
import os
import re
import subprocess
# import string

def get_name_and_version(name):
	if not name[-1].isdigit():
		base_name = name.rstrip("_- ")  # string.punctuation
		return base_name, 0
	base_name = re.sub("[\s_-]*[vV]?\d+$", "", name)
	v = int(re.search("\d+$", name).group())
	return base_name, v

def get_newest_version():
	folder_path = bpy.path.abspath("//")
	# if not folder_path:
	# 	return True
	name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
	current_name, current_version = get_name_and_version(name)
	# newest_version = -1
	for file in os.listdir(folder_path):
		split = os.path.splitext(file)
		if split[-1].lower() == ".blend":
			new_name, new_version = get_name_and_version(split[0])
			if current_name != new_name:
				continue
			if current_version < new_version:
				current_version = new_version
	return current_version

def get_newest_file():
	blend_file = bpy.data.filepath
	print(blend_file)
	name = os.path.splitext(bpy.path.basename(blend_file))[0]
	current_name, current_version = get_name_and_version(name)
	folder_path = bpy.path.abspath("//")
	for file in os.listdir(folder_path):
		split = os.path.splitext(file)
		if split[-1].lower() == ".blend":
			new_name, new_version = get_name_and_version(split[0])
			if current_name != new_name:
				continue
			if current_version < new_version:
				blend_file = os.path.join(folder_path, file)
				print(blend_file)
	return blend_file

def is_current_file_version():
	if not bpy.data.is_saved:
		return True
	name = os.path.splitext(bpy.path.basename(bpy.data.filepath))[0]
	current_version = get_name_and_version(name)[1]
	newest_version = get_newest_version()
	return current_version == newest_version

def version_up(name):
	# if it doesn't have a version, add it
	if not name[-1].isdigit():
		return name + "_v02"  # v001 or v002 ?
	# otherwise increment by 1
	base_name = re.sub("\d+$", "", name)
	v = re.search("\d+$", name).group()
	new_v = str(int(v) + 1).zfill(len(v))
	return base_name + new_v




class AX_OT_save_as_new_version(bpy.types.Operator):
	
	bl_idname = "ax.save_as_new_version"
	bl_label = "Save as New Version"
	bl_description = "This will work even if the current file is not the latest version"
	bl_options = {'REGISTER', 'UNDO'}
	
	# bpy.data.is_dirty
	def execute(self, context):
		latest_file = get_newest_file()

		folder_path = bpy.path.abspath("//")
		name = os.path.splitext(bpy.path.basename(latest_file))[0]
		name = version_up(name) + ".blend"
		new_filepath = os.path.join(folder_path, name)
		bpy.ops.wm.save_as_mainfile(filepath=new_filepath)
		return {'FINISHED'}

class AX_OT_go_to_latest_version(bpy.types.Operator):
	
	bl_idname = "ax.go_to_latest_version"
	bl_label = "Jump to Latest Version"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		latest_file = get_newest_file()
		bpy.ops.wm.open_mainfile(filepath=latest_file)
		return {'FINISHED'}

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
	bl_label = "Locate BLEND"
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