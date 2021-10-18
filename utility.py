import bpy
import bmesh
import re

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





# class PhysicButtonsPanel:
#     bl_space_type = 'PROPERTIES'
#     bl_region_type = 'WINDOW'
#     bl_context = "physics"

#     @classmethod
#     def poll(cls, context):
#         ob = context.object
#         return (ob and ob.type == 'MESH') and (context.engine in cls.COMPAT_ENGINES) and (context.cloth)

# class PHYSICS_PT_cloth(PhysicButtonsPanel, Panel):
#     bl_label = "Cloth"
#     COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

#     def draw_header_preset(self, _context):
#         CLOTH_PT_presets.draw_panel_header(self.layout)

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True

#         md = context.cloth
#         cloth = md.settings

#         layout.active = cloth_panel_enabled(md)

#         flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)

#         col = flow.column()
#         col.prop(cloth, "quality", text="Quality Steps")
#         col = flow.column()
#         col.prop(cloth, "time_scale", text="Speed Multiplier")


# class PHYSICS_PT_cloth_physical_properties(PhysicButtonsPanel, Panel):
#     bl_label = "Physical Properties"
#     bl_parent_id = 'PHYSICS_PT_cloth'
#     COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}

#     def draw(self, context):
#         layout = self.layout
#         layout.use_property_split = True

#         md = context.cloth
#         cloth = md.settings

#         layout.active = cloth_panel_enabled(md)

#         flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)

#         col = flow.column()
#         col.prop(cloth, "mass", text="Vertex Mass")
#         col = flow.column()
#         col.prop(cloth, "air_damping", text="Air Viscosity")
#         col = flow.column()
#         col.prop(cloth, "bending_model")