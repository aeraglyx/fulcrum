import bpy
import bmesh
import re
import random


class AX_OT_locate_vertex(bpy.types.Operator):

	bl_idname = "ax.locate_vertex"
	bl_label = "Locate Vertex"
	bl_description = "Select a vertex based on its ID"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.object and context.object.type == 'MESH'
	
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
		return context.active_object and context.object.type == 'MESH'
	
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
		
		# print(f"{cloth_modif = }")
		
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

class AX_OT_hybrid_subdiv(bpy.types.Operator):

	bl_idname = "ax.hybrid_subdiv"
	bl_label = "Hybrid Subdivision"
	bl_description = "..."
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return bool(context.object)

	subdivision: bpy.props.IntProperty(
		name = "Subdivision",
		description = "Number of total subdivisions",
		min = 0, default = 4, soft_max = 6
	)
	sharp_or_smooth: bpy.props.FloatProperty(
		name = "Sharp / Smooth",
		description = "Number of total subdivisions",
		min = 0.0, default = 0.5, max = 1.0,
		subtype = 'FACTOR'
	)
	shade_smooth: bpy.props.BoolProperty(
		name = "Shade Smooth",
		description = "Turn on shade smoothing",
		default = True
	)

	def execute(self, context):

		obj = context.object

		if self.subdivision:

			smooth_subdiv = round(self.subdivision * self.sharp_or_smooth)
			sharp_subdiv = self.subdivision - smooth_subdiv

			if sharp_subdiv:
				subsurf_modif = obj.modifiers.get("Subdivision Sharp") or obj.modifiers.new("Subdivision Sharp", 'SUBSURF')
				subsurf_modif.subdivision_type = 'SIMPLE'
				subsurf_modif.levels = sharp_subdiv
				subsurf_modif.render_levels = sharp_subdiv
			
			if smooth_subdiv:
				subsurf_modif = obj.modifiers.get("Subdivision Smooth") or obj.modifiers.new("Subdivision Smooth", 'SUBSURF')
				subsurf_modif.subdivision_type = 'CATMULL_CLARK'
				subsurf_modif.levels = smooth_subdiv
				subsurf_modif.render_levels = smooth_subdiv
		
		if self.shade_smooth:
			bpy.ops.object.shade_smooth()
		else:
			bpy.ops.object.shade_flat()

		return {'FINISHED'}

	def draw(self, context):

		layout = self.layout

		layout.use_property_split = True
		layout.use_property_decorate = False

		col = layout.column(align = True)
		col.prop(self, "subdivision")
		col.prop(self, "sharp_or_smooth")
		
		layout.prop(self, "shade_smooth")

class AX_OT_vert_group_2_col(bpy.types.Operator):
	
	bl_idname = "ax.vert_group_2_col"
	bl_label = "Groups to Colors"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return len(bpy.context.active_object.vertex_groups) # HACK idk

	def execute(self, context):

		groups = bpy.context.active_object.vertex_groups
		colors = bpy.context.active_object.data.vertex_colors

		need_to_switch_back = False
		if bpy.context.mode != 'PAINT_VERTEX':
			bpy.ops.paint.vertex_paint_toggle()
			need_to_switch_back = True

		for group in groups:

			# FIXME max 8 vert. colours
			
			col = colors.new()
			col.name = group.name

			groups.active = group
			colors.active = col

			bpy.ops.paint.vertex_color_from_weight()  # FIXME probably does not work for "empty" groups (new ones)

		if need_to_switch_back:
			bpy.ops.paint.vertex_paint_toggle()

		self.report({'INFO'}, f"Done.")

		return {'FINISHED'}

class AX_OT_duplicates_to_instances(bpy.types.Operator):
	
	bl_idname = "ax.duplicates_to_instances"
	bl_label = "Duplicates to Instances"
	bl_description = "Find objects with with duplicate meshes, make them use the same instance of mesh and remove the redundant data"
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):

		def same_mesh(mesh_1, mesh_2):  # TODO make more robust
			
			size = len(mesh_1.vertices)
			if size != len(mesh_2.vertices):
				return False
			
			num_list = range(0, size)
			n = 64
			if size > n:
				num_list = sorted(random.sample(num_list, n))
			for i in num_list:
				if mesh_1.vertices[i].co != mesh_2.vertices[i].co:
					return False
			
			if set(mesh_1.materials) != set(mesh_2.materials):
				return False
			
			return True
		
		def purge_meshes():
			for block in bpy.data.meshes:
				if block.users == 0:
					bpy.data.meshes.remove(block)
		
		purge_meshes()
		n1 = len(bpy.data.meshes)

		objects = [obj for obj in bpy.data.objects if obj.type == 'MESH']
		unique_meshes = []

		for obj in objects:
			mesh = obj.data
			if mesh not in unique_meshes:
				unique = True
				for unique_mesh in unique_meshes:
					if same_mesh(mesh, unique_mesh):
						obj.data = unique_mesh
						unique = False
						break
			if unique:
				unique_meshes.append(mesh)
		
		purge_meshes()
		n2 = len(bpy.data.meshes)
		
		self.report({'INFO'}, f"{n1 - n2} mesh{'' if n2 == 1 else 'es'} deleted.")

		return {'FINISHED'}

class AX_OT_obj_backup(bpy.types.Operator):
	
	bl_idname = "ax.obj_backup"
	bl_label = "Backup Object"
	bl_description = ""
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		
		obj_orig = context.active_object
		obj_copy = obj_orig.copy()

		obj_copy.data = obj_orig.data.copy()
		if obj_orig.animation_data:
			obj_copy.animation_data.action = obj_orig.animation_data.action.copy()
		obj_copy.name = obj_orig.name + "_backup"
		
		collection = obj_orig.users_collection[0]
		collection.objects.link(obj_copy)
		context.view_layer.objects.active = obj_orig
		for layer in context.scene.view_layers:
			obj_copy.select_set(False, view_layer=layer)
			obj_copy.hide_set(True, view_layer=layer)
		obj_copy.hide_viewport = True
		obj_copy.hide_render = True

		self.report({'INFO'}, f"\"{obj_orig.name}\" backed up successfully!")

		return {'FINISHED'}