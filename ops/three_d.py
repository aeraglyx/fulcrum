import bpy
import bmesh
import re
import random


class FULCRUM_OT_locate_vertex(bpy.types.Operator):

	bl_idname = "fulcrum.locate_vertex"
	bl_label = "Locate Vertex"
	bl_description = "Select a vertex based on its ID"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.object and context.object.type == 'MESH'
	
	index: bpy.props.IntProperty(name="Index", min=0, default=0)

	def execute(self, context):

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode='EDIT')

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

class FULCRUM_OT_locate_vertices(bpy.types.Operator):

	bl_idname = "fulcrum.locate_vertices"
	bl_label = "Locate Vertices"
	bl_description = "Select vertices based on a list of IDs"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object and context.object.type == 'MESH'
	
	indices_str: bpy.props.StringProperty(name="Indices", default="")

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

		# TODO combine single vertex and multiple vertices search to one op?
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "indices_str")

class FULCRUM_OT_vert_group_2_col(bpy.types.Operator):
	
	bl_idname = "fulcrum.vert_group_2_col"
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

class FULCRUM_OT_duplicates_to_instances(bpy.types.Operator):
	
	bl_idname = "fulcrum.duplicates_to_instances"
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

class FULCRUM_OT_obj_backup(bpy.types.Operator):
	
	bl_idname = "fulcrum.obj_backup"
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

class FULCRUM_OT_edit_light_power(bpy.types.Operator):
	
	bl_idname = "fulcrum.edit_light_power"
	bl_label = "Edit Light Power"
	bl_description = "Proportionally edit light intensities of all selected lights"
	bl_options = {'REGISTER', 'UNDO'}
	
	multiplier: bpy.props.FloatProperty(
		name="Multiplier",
		description="Light power multiplier. 2.0 means double the intensity etc",
		soft_min=0.0, default=1.0,
	)

	def execute(self, context):
		objects = context.selected_objects
		lights = {obj.data for obj in objects if obj.type == 'LIGHT'}
		for light in lights:
			light.energy *= self.multiplier
		# TODO make it work for emission shaders
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)
	
	def draw(self, context):
		layout = self.layout
		layout.prop(self, "multiplier")

class FULCRUM_OT_reduce_materials(bpy.types.Operator):

	bl_idname = "fulcrum.reduce_materials"
	bl_label = "(Reduce Materials)"
	bl_description = "Remove duplicate materials. It's bugged"
	bl_options = {'REGISTER', 'UNDO'}

	first_or_last: bpy.props.EnumProperty(
		name = "Pick",
		description = "...",
		items = [
			('FIRST', "First", ""),
			('LAST', "Last", "")
		],
		default = 'FIRST',
	)

	def execute(self, context):

		base_names_dict = {}
		new_dict = {}
		slots_to_remove = []

		# base_name(slot)

		for obj in context.selected_objects:  # TODO only data which supports materials ?
			slots = obj.material_slots
			for slot in slots:
				name = slot.material.name
				if name[-3:].isdigit() and name[-4] == '.':
					base_name = name[:-4]
					version = name[-3:]
				else:
					base_name = name
					version = ""
				if base_name in base_names_dict:
					base_names_dict[base_name].append(version)
				else:
					base_names_dict[base_name] = [version]
				# TODO iterativne davat min/max, takze by se nepotrebovala dalsi for loop ?
		
		for base_name in base_names_dict:
			versions = base_names_dict[base_name]
			def ordering(x):
				return -1 if x == "" else int(x)
			if self.first_or_last == 'FIRST':
				version_yes = min(versions, key=ordering)
			else:
				version_yes = max(versions, key=ordering)
			slot_yes = base_name if version_yes == "" else ".".join(base_name, version_yes)
			new_dict[base_name] = slot_yes
				
		for obj in context.selected_objects:
			bpy.context.view_layer.objects.active = obj
			slots = obj.material_slots
			slot_names = [slot.material.name for slot in slots]
			for slot in slots:

				name = slot.material.name
				if name[-3:].isdigit() and name[-4] == '.':
					base_name = name[:-4]
				else:
					base_name = name
				
				if new_dict[base_name] == name:
					continue

				index_noo = slot_names.index(name)
				index_yes = slot_names.index(new_dict[base_name])
				
				faces = [face for face in bpy.context.object.data.polygons if face.material_index == index_noo]
				for face in faces:
					face.material_index = index_yes
				
				slots_to_remove.append(slot.name)

			for slot in slots_to_remove:
				if slot in [x.name for x in bpy.context.object.material_slots]:
					obj.active_material_index = [x.material.name for x in obj.material_slots].index(slot)
					bpy.ops.object.material_slot_remove()  # context zasrany, nejde to na vic objektu, passnout tomu context?

			# bpy.ops.object.material_slot_remove_unused()


		return {'FINISHED'}

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "first_or_last")