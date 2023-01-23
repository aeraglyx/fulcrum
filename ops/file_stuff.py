import bpy
import os
import re
import subprocess
from ..functions import *
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




class AX_OT_save_as_new_version(bpy.types.Operator):
	
	bl_idname = "ax.save_as_new_version"
	bl_label = "Save as New Version"
	bl_description = "This will work even if the current file is not the latest version"

	@classmethod
	def poll(cls, context):
		return bpy.data.is_saved
	
	def execute(self, context):
		latest_file = get_newest_file()
		folder_path = bpy.path.abspath("//")
		name = os.path.splitext(bpy.path.basename(latest_file))[0]
		name = version_up(name) + ".blend"
		new_filepath = os.path.join(folder_path, name)
		bpy.ops.wm.save_as_mainfile(filepath=new_filepath)
		# TODO save versions in a subfolder
		return {'FINISHED'}

class AX_OT_go_to_latest_version(bpy.types.Operator):
	
	bl_idname = "ax.go_to_latest_version"
	bl_label = "Jump to Latest Version"
	bl_description = "Opens the latest version of this file from the same directory"

	@classmethod
	def poll(cls, context):
		return bpy.data.is_saved

	def execute(self, context):
		latest_file = get_newest_file()
		bpy.ops.wm.open_mainfile(filepath=latest_file)
		return {'FINISHED'}

class AX_OT_open_blend_dir(bpy.types.Operator):
	
	bl_idname = "ax.open_blend_dir"
	bl_label = "Find .blend File"
	bl_description = "Opens file explorer with the current Blender file selected"

	@classmethod
	def poll(cls, context):
		return bpy.data.is_saved

	def execute(self, context):
		path = bpy.data.filepath
		subprocess.Popen('explorer /select,"' + path + '"')
		return {'FINISHED'}

class AX_OT_open_script_dir(bpy.types.Operator):
	
	bl_idname = "ax.open_script_dir"
	bl_label = "Find Script Directory"
	bl_description = "Opens folder with addons and themes"

	def execute(self, context):
		path = bpy.utils.script_path_user()
		os.startfile(path)
		return {'FINISHED'}






# import subprocess
# import sys
# import os

# python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
# subprocess.call([python_exe, "-m", "ensurepip"])
# subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
# subprocess.call([python_exe, "-m", "pip", "install", "urllib"])

import requests, zipfile, io, shutil, addon_utils

class AX_OT_update_fulcrum(bpy.types.Operator):
	
	bl_idname = "ax.update_fulcrum"
	bl_label = "Update Fulcrum"
	bl_description = "Update this addon. Blender will need to be restarted"

	def execute(self, context):
		repo_download_link = "https://github.com/aeraglyx/fulcrum/archive/refs/heads/master.zip"
		fulcrum_path = os.path.join(bpy.utils.script_path_user(), "addons", "fulcrum")
		nested_path = os.path.join(fulcrum_path, "fulcrum-master")
		
		old_version = get_addon_version("Fulcrum")

		shutil.rmtree(fulcrum_path, ignore_errors=True)

		# with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
		# 	zip_ref.extractall(fulcrum_path)
		r = requests.get(repo_download_link)
		z = zipfile.ZipFile(io.BytesIO(r.content))
		z.extractall(fulcrum_path)

		for filename in os.listdir(nested_path):
			src = os.path.join(nested_path, filename)
			dst = os.path.join(fulcrum_path, filename)
			shutil.move(src, dst)
		
		os.rmdir(nested_path)

		new_version = get_addon_version("Fulcrum")

		context.scene.fulcrum.restart_needed = True
		self.report({'INFO'}, f"Updated from {old_version} to {new_version}. Blender restart needed.")
		bpy.ops.script.reload()

		return {'FINISHED'}