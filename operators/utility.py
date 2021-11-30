import bpy
import bmesh
import re
import os

class AX_OT_locate_vertex(bpy.types.Operator):

	bl_idname = "ax.locate_vertex"
	bl_label = "Locate Vertex"
	bl_description = "Select a vertex based on its ID"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object
	
	index: bpy.props.IntProperty(
		name = "Index",
		min = 0, default = 0
	)

	def execute(self, context):

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode = 'EDIT')

		statistics_str = context.scene.statistics(context.view_layer)
		total_verts = int(re.search("Verts:\d+/(\d+)", statistics_str).groups()[0])
		
		if self.index < total_verts:  # len(verts)
			
			obj = context.active_object
			bm = bmesh.from_edit_mesh(obj.data)

			for vert in bm.verts:
				if vert.index == self.index:
					vert_found = vert
					vert_found.select_set(True)
				else:
					vert.select_set(False)
			
			bm.select_flush_mode()
			bmesh.update_edit_mesh(obj.data)
			
			location = obj.matrix_world @ vert_found.co
			context.scene.cursor.location = location

			pos = [round(x, 2) for x in list(location)]
			self.report({'INFO'}, f"Found vertex {self.index} at {pos}.")
			
		else:
			self.report({'WARNING'}, f"Index out of range.")
			return {'CANCELLED'}
		
		bpy.ops.object.mode_set(mode = mode_prev)

		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "index")


class AX_OT_locate_vertices(bpy.types.Operator):

	bl_idname = "ax.locate_vertices"
	bl_label = "Locate Vertices"
	bl_description = "Select vertices based on a list of IDs"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object
	
	indices_str: bpy.props.StringProperty(
		name = "Indices",
		default = ""
	)

	def execute(self, context):

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode = 'EDIT')

		obj = context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		verts = bm.verts

		indices = re.findall(r"\d+", self.indices_str)
		indices = [int(i) for i in indices]
		indices = list(set(indices))

		found = 0
		for vert in verts:
			if vert.index in indices:
				vert.select_set(True)
				found += 1
			else:
				vert.select_set(False)
		
		bm.select_flush_mode()
		bmesh.update_edit_mesh(obj.data)

		self.report({'INFO'}, f"Found {found} out of {len(indices)} vertices.")
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "indices_str")


class AX_OT_cloth_vert_mass(bpy.types.Operator):

	# TODO slider in UI and automatically update ?

	bl_idname = "ax.cloth_vert_mass"
	bl_label = "Vertex Mass from Object"
	bl_description = "Works but not really"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return True  # TODO physics cloth
	
	obj_mass: bpy.props.FloatProperty(
		name = "Object Mass",
		min = 0.0, default = 1.0,
		unit = 'MASS'
	)

	def execute(self, context):

		obj = context.object
		tmp_obj = obj.copy()
		tmp_obj.name = "ax_tmp_object"
		tmp_mesh = obj.data.copy()
		tmp_obj.data = tmp_mesh
		tmp_obj.data.name = "ax_tmp_mesh"

		modifiers = tmp_obj.modifiers
	
		cloth_modif = None
		to_apply = []
		to_delete = []

		for modif in modifiers:
			if cloth_modif:
				to_delete.append(modif)
			else:
				to_apply.append(modif)
			if modif.type == 'CLOTH':
				to_delete.append(modif)
				cloth_modif = modif
		
		print(f"{cloth_modif = }")
		
		for modif in to_delete:
			modifiers.remove(modif)

		bm = bmesh.new()
		depsgraph = context.evaluated_depsgraph_get()
		bm.from_object(tmp_obj, depsgraph)
		vert_count = len(bm.verts)
		bm.clear()

		orig_cloth_modif = None
		for modif in obj.modifiers:
			if modif.type == 'CLOTH':
				orig_cloth_modif = modif
				break
		
		bpy.data.objects.remove(tmp_obj)
		bpy.data.meshes.remove(tmp_mesh)

		orig_cloth_modif.settings.mass = self.obj_mass / vert_count

		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "obj_mass")


class AX_OT_set_auto_smooth(bpy.types.Operator):
	
	bl_idname = "ax.set_auto_smooth"
	bl_label = "Set Auto Smooth"
	bl_description = ""
	bl_options = {'REGISTER', 'UNDO'}

	# TODO poll (only in obj right now) mesh active

	angle: bpy.props.FloatProperty(
		name = "Angle",
		min = 0.0, default = 0.523598775598, max = 3.141592653589,
		subtype = 'ANGLE',
		unit = 'ROTATION'
	)

	def execute(self, context):

		mesh = context.object.data

		for polygon in mesh.polygons:
			polygon.use_smooth = True

		mesh.use_auto_smooth = True
		mesh.auto_smooth_angle = self.angle
		
		return {'FINISHED'}
	
	def draw(self, context):
		
		layout = self.layout
		# layout.use_property_split = True
		# layout.use_property_decorate = False
		col = layout.column(align = True)
		col.prop(self, "angle")


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

		path = os.path.realpath(bpy.path.abspath("//"))  # XXX points to AHK dir when not saved
		os.startfile(path)  # TODO select the blend?
		
		return {'FINISHED'}